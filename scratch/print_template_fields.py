import openpyxl

def main():
    wb = openpyxl.load_workbook("Sample Fields.xlsx")
    sheet = wb.active
    print("=== Fields in Column A ===")
    for r in range(1, 100):
        val = sheet.cell(row=r, column=1).value
        if val is not None:
            print(f"Row {r:2d}: {val}")

if __name__ == "__main__":
    main()
