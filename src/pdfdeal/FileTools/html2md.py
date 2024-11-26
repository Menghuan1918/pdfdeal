from bs4 import BeautifulSoup


def html_table_to_md(text: str) -> str:
    """Convert HTML tables to Markdown tables in the given text.

    Args:
        text (str): Text containing HTML tables

    Returns:
        str: Text with HTML tables converted to Markdown format
    """
    soup = BeautifulSoup(text, "html.parser")
    tables = soup.find_all("table")

    for table in tables:
        md_table = []
        max_cols = 0

        # Get all rows
        rows = table.find_all("tr")
        if not rows:
            continue

        for row in rows:
            cols = 0
            for cell in row.find_all(["td", "th"]):
                colspan = int(cell.get("colspan", 1))
                cols += colspan
            max_cols = max(max_cols, cols)

        for row in rows:
            row_data = []
            cells = row.find_all(["td", "th"])

            col_count = 0
            for cell in cells:
                content = cell.get_text().strip()
                colspan = int(cell.get("colspan", 1))
                for _ in range(colspan):
                    row_data.append(content)
                    col_count += 1

            while col_count < max_cols:
                row_data.append("")
                col_count += 1

            md_table.append("| " + " | ".join(row_data) + " |")

            if len(md_table) == 1:
                md_table.append("| " + " | ".join(["---"] * max_cols) + " |")

        # Replace the HTML table with markdown table
        md_table_str = "\n".join(md_table)
        table.replace_with(md_table_str)

    return str(soup)
