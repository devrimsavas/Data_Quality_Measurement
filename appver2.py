import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk  

# Initialize Tkinter window
root = tk.Tk()
root.title("Dynamic Data Quality Checker")
root.geometry("1000x900") 
root.configure(bg="#f0f0f0")

# Global variable for DataFrame
df = None

# Function to load CSV file
def load_file():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        df = pd.read_csv(file_path)
        messagebox.showinfo("File Loaded", "CSV file loaded successfully!")
    else:
        messagebox.showwarning("No File", "No file was selected.")

# Dynamically run data quality checks based on column types
def run_checks():
    global df
    if df is None:
        messagebox.showerror("Error", "Please load a CSV file first.")
        return

    # Clear the Treeview table before adding new results
    for row in result_table.get_children():
        result_table.delete(row)

    # Initialize total errors counter
    total_errors = 0  

    # Check for missing values across all columns
    missing_values = df.isnull().sum().sum()
    result_table.insert("", "end", values=("Missing Values", missing_values))
    total_errors += missing_values

    # Check for duplicate records
    duplicates = df[df.duplicated()]
    duplicate_count = len(duplicates)
    result_table.insert("", "end", values=("Duplicate Records", duplicate_count))
    total_errors += duplicate_count

    # Analyze each column dynamically based on data type
    for column in df.columns:
        column_data = df[column]
        
        # Check for Date Columns
        if pd.api.types.is_datetime64_any_dtype(column_data):
            result_table.insert("", "end", values=(f"{column} Date Format", "Consistent"))
        elif pd.api.types.is_object_dtype(column_data) and column_data.str.match(r'\d{2}/\d{2}/\d{4}').all():
            try:
                pd.to_datetime(column_data, format='%d/%m/%Y', errors='raise')
                result_table.insert("", "end", values=(f"{column} Date Format", "Consistent"))
            except ValueError:
                result_table.insert("", "end", values=(f"{column} Date Format", "Inconsistent"))
                total_errors += 1

        # Check for Numeric Columns with Out-of-Range Values
        elif pd.api.types.is_numeric_dtype(column_data):
            out_of_range_count = column_data[(column_data < 0) | (column_data > 120)].count()
            result_table.insert("", "end", values=(f"{column} Out-of-Range Values", out_of_range_count))
            total_errors += out_of_range_count

        # Check for Text/Categorical Columns with Duplicates or Specific Categories
        elif pd.api.types.is_string_dtype(column_data):
            unique_values = column_data.nunique()
            duplicate_text_count = len(column_data) - unique_values
            result_table.insert("", "end", values=(f"{column} Non-Unique Text Values", duplicate_text_count))
            total_errors += duplicate_text_count

    # Calculate and display Ratio of Amount of Data to Errors
    total_data_points = df.size  # Total cells in the DataFrame (rows * columns)
    error_ratio = total_errors / total_data_points if total_data_points > 0 else 0
    result_table.insert("", "end", values=("Error Ratio", f"{error_ratio:.2%}"))


# Display the reference image permanently
ref_image = Image.open("reftable.png")
ref_image = ref_image.resize((600, 300), Image.LANCZOS)
img = ImageTk.PhotoImage(ref_image)

# Frame for Image
img_frame = ttk.Frame(root, padding="10", relief="solid")
img_frame.pack(pady=10)
img_label = tk.Label(img_frame, image=img, bg="white")
img_label.image = img
img_label.pack()

# Frame for Buttons
button_frame = ttk.Frame(root, padding="10")
button_frame.pack(pady=10)

load_button = ttk.Button(button_frame, text="Load CSV File", command=load_file)
load_button.grid(row=0, column=0, padx=5)

run_button = ttk.Button(button_frame, text="Run Data Quality Checks", command=run_checks)
run_button.grid(row=0, column=1, padx=5)

# Table Frame for Results
table_frame = ttk.Frame(root, padding="10", relief="solid")
table_frame.pack(pady=20)

# Treeview table display results
columns = ("Check", "Result")
result_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
result_table.heading("Check", text="Data Quality Check")
result_table.heading("Result", text="Result")

# Set column width
result_table.column("Check", width=300, anchor="w")
result_table.column("Result", width=200, anchor="center")

# Add alternating row colors
def style_rows():
    for i, row in enumerate(result_table.get_children()):
        if i % 2 == 0:
            result_table.tag_configure("evenrow", background="#f9f9f9")
        else:
            result_table.tag_configure("oddrow", background="#e0e0e0")
        result_table.item(row, tags=("evenrow" if i % 2 == 0 else "oddrow"))

result_table.pack()
style_rows()

# Run the Tkinter event loop
root.mainloop()
