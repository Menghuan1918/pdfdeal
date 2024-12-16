import subprocess
import logging
from pathlib import Path
from ..file_tools import auto_split_mds
from ..file_tools import mds_replace_imgs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def convert_pdf_to_md(input_dir: str, output_dir: str, process_each=False, uploader=None, qps=0, steps_to_run=None,threads=5):
    """
    将PDF转换为Markdown文件
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        process_each: 是否对每个转换后的文件立即进行后续处理
        uploader: 图片上传器（当process_each=True且需要处理图片时需要）
        qps: 上传限速（当process_each=True且需要处理图片时可用）
        steps_to_run: 要运行的步骤列表，如 [1, 3] 表示只运行第1步和第3步
        threads：mds_replace_imgs中使用的线程数，默认不修改
    """
    logging.info("Step 1: Converting PDFs to Markdown...")
    result = {
        'success': False,
        'success_files': [],
        'failed_files': [],
        'error': None
    }
    
    # 如果没有指定步骤，默认运行所有步骤
    if steps_to_run is None:
        steps_to_run = [1, 2, 3]
    
    try:
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # 获取所有PDF文件
        pdf_files = list(input_path.glob('*.pdf'))
        logging.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            logging.info(f"\nProcessing: {pdf_file}")
            try:
                # 构建输出文件路径
                output_md = output_path / f"{pdf_file.stem}"
                logging.info(f"Output path: {output_md}")
                
                # 执行PDF到MD的转换（第1步总是需要执行）
                subprocess.run([
                    'marker_single',
                    str(pdf_file),
                    '--output_dir', str(output_path),
                    '--output_format', 'markdown',
                    '--force_ocr'
                ], check=True)
                
                result['success_files'].append(str(pdf_file))
                
                # 如果启用了即时处理，对刚转换的文件进行处理
                if process_each and output_md.exists():
                    logging.info(f"Performing immediate processing for {pdf_file}")
                    
                    # 创建临时目录用于单文件处理
                    temp_dir = output_path / "temp_processing"
                    temp_dir.mkdir(exist_ok=True)
                    logging.info(f"Created temp directory: {temp_dir}")
                    
                    # 复制文件到临时目录
                    temp_md = temp_dir / output_md.name
                    import shutil
                    shutil.copytree(output_md, temp_md)
                    
                    # 根据选择的步骤执行处理
                    if 2 in steps_to_run:
                        logging.info(f"Running step 2 (split) for {pdf_file}")
                        # 使用auto_split_mds进行拆分
                        success_files, failed_files, has_error = auto_split_mds(
                            str(temp_dir),
                            mode="title",
                            out_type="replace",
                            recursive=True
                        )
                        if has_error:
                            logging.warning(f"Split partially failed for {pdf_file}")
                            for failed in failed_files:
                                if failed.get('error'):
                                    logging.warning(f"Split error: {failed['error']}")
                    
                    if 3 in steps_to_run:
                        upload_func = uploader
        
                        if qps > 0:
                            from .rate_limter import RateLimiter
                            rate_limiter = RateLimiter(qps)
                            original_upload = upload_func
                            
                            def rate_limited_upload(*args, **kwargs):
                                rate_limiter.acquire()
                                return original_upload(*args, **kwargs)
            
                            upload_func = rate_limited_upload

                        logging.info(f"Running step 3 (image processing) for {pdf_file}")
                        if upload_func:
                            try:
                                success_files, failed_files, has_error = mds_replace_imgs(
                                    path=str(temp_dir),
                                    replace=upload_func,
                                    threads=threads
                                )
                                if has_error:
                                    logging.warning(f"Image processing partially failed for {pdf_file}")
                                    for failed in failed_files:
                                        if failed.get('error'):
                                            logging.warning(f"Image processing error: {failed['error']}")
                            except Exception as e:
                                logging.warning(f"Image processing failed for {pdf_file}: {e}")
                    
                    # 处理完成，将处理后的文件移回原位置
                    shutil.rmtree(output_md, ignore_errors=True)  # 删除原目录
                    shutil.copytree(temp_md, output_md)
                    logging.info(f"Moved processed file back to: {output_md}")
                    
                    # 清理临时目录
                    shutil.rmtree(temp_dir)
                    logging.info("Cleaned up temp directory")
                
            except subprocess.CalledProcessError as e:
                result['failed_files'].append(str(pdf_file))
                logging.error(f"Error converting {pdf_file}: {e}")
                continue
            except Exception as e:
                logging.error(f"Unexpected error processing {pdf_file}: {e}")
                continue
        
        result['success'] = len(result['failed_files']) == 0
        logging.info(f"\nProcessing completed. Successful: {len(result['success_files'])}, Failed: {len(result['failed_files'])}")
        
    except Exception as e:
        result['error'] = str(e)
        result['success'] = False
        logging.error(f"Fatal error: {e}")
    
    return result