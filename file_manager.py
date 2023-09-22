import openpyxl
import pandas as pd
import datetime
import owncloud
import os

class FileManager:
    workbook = openpyxl.Workbook()
    input_file_path : str
    output_file_path : str
    def __init__(self, input_file_path, output_file_path):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.oc = owncloud.Client.from_public_link('https://tuc.cloud/index.php/s/nisTB2KdNHHzgGy', folder_password = "dfg1325FDsg221")  # connect to the cloud

    def append_row_to_excel(self, value, sheet_name):
        timestamp = str(datetime.datetime.now())
        try:
            # Load the existing Excel workbook if it exists
            workbook = openpyxl.load_workbook(self.output_file_path)
        except FileNotFoundError:
            # Create a new workbook if the file doesn't exist
            workbook = openpyxl.Workbook()

        # Check if the specified sheet already exists
        if sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
        else:
            # Create a new sheet if it doesn't exist
            sheet = workbook.create_sheet(title=sheet_name)

        # Calculate the index for the new row (after the last row)
        insert_index = sheet.max_row + 1

        # Create a DataFrame with the new row data
        data = {'Value': value, 'Timestamp': timestamp}
        df_row = pd.DataFrame([data])

        # Convert the DataFrame row to a list
        row_values = df_row.values.tolist()[0]

        # Insert a new row at the calculated index
        sheet.insert_rows(insert_index)

        # Populate the cells in the new row with data
        for col, value in enumerate(row_values, start=1):
            sheet.cell(row=insert_index, column=col, value=value)

        # Save the modified workbook
        workbook.save(self.output_file_path)

        # Close the workbook
        workbook.close()

    def get_sheet_names(self) -> list[str]:
        if self.input_file_path:
            wb = openpyxl.load_workbook(self.input_file_path)
            sheet_names = wb.sheetnames
            wb.close()
            return sheet_names
        
    def appendQRData(self, value, sheetName):
        try:
            self.downloadRemoteFile(self.output_file_path)
        except:
            return "Error Downloading File"
        
        try:
            self.append_row_to_excel(value, sheetName)
        except:
            return "Error appending to File"
        
        try:
            self.upload_to_the_cloud(self.output_file_path)
            return "Saved on the cloud"
        except:
            return "Saved locally"


    def get_sessions(self, selected_sheet: str) -> list[str]:
        if selected_sheet:
            wb = openpyxl.load_workbook(self.input_file_path)
            sheet = wb[selected_sheet]
            rows = sheet.iter_rows(values_only=True)
            row_values = [", ".join(map(str, row)) for row in rows]
            wb.close() 
            return row_values
        
    def downloadRemoteFile(self, saveFile: str):
        self.oc.get_file(saveFile, saveFile) # download remote file
    
    def upload_to_the_cloud(self, file_name):
        self.oc.drop_file(file_name)  # upload file to cloud
        os.remove(file_name)     # delete local file when upload successful