import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk  # Import ttk for Treeview
from PIL import Image, ImageTk  

# Initialize Tkinter window
root = tk.Tk()
root.title("Data Quality Checker ")
root.geometry("1000x900")  #size can be adjustable 

# Global variable for  DataFrame
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

# Run data quality checks and display in table format
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

    # Calculate and display each check result
    # Check for missing values
    missing_values = df.isnull().sum().sum()
    result_table.insert("", "end", values=("Missing Values", missing_values))
    total_errors += missing_values

    # Check for duplicate records
    duplicates = df[df.duplicated()]
    duplicate_count = len(duplicates)
    result_table.insert("", "end", values=("Duplicate Records", duplicate_count))
    total_errors += duplicate_count

    # Check date format consistency
    date_columns = ['Join Date', 'Last Payment Date']
    for column in date_columns:
        try:
            pd.to_datetime(df[column], format='%d/%m/%Y', errors='raise')
            result_table.insert("", "end", values=(f"'{column}' Date Format", "Consistent"))
        except ValueError:
            result_table.insert("", "end", values=(f"'{column}' Date Format", "Inconsistent"))
            total_errors += 1  # Count format inconsistency as an error

    # Check for out-of-range age values
    out_of_range_age = df[(df['Age'] < 0) | (df['Age'] > 120)]
    out_of_range_age_count = len(out_of_range_age)
    result_table.insert("", "end", values=("Out-of-range Age Values", out_of_range_age_count))
    total_errors += out_of_range_age_count

    # Check for unique User IDs
    unique_user_ids = df['User ID'].nunique()
    total_user_ids = df['User ID'].size
    non_unique_ids = total_user_ids - unique_user_ids
    result_table.insert("", "end", values=("Non-unique User IDs", non_unique_ids))
    total_errors += non_unique_ids

    # Check for invalid subscription types
    valid_subscription_types = ['Basic', 'Standard', 'Premium']
    invalid_subscription_types = df[~df['Subscription Type'].isin(valid_subscription_types)]
    invalid_subscription_count = len(invalid_subscription_types)
    result_table.insert("", "end", values=("Invalid Subscription Types", invalid_subscription_count))
    total_errors += invalid_subscription_count

    # Calculate and display Ratio of Amount of Data to Errors
    total_data_points = df.size  # Total cells in the DataFrame (rows * columns)
    error_ratio = total_errors / total_data_points if total_data_points > 0 else 0
    result_table.insert("", "end", values=("Error Ratio", f"{error_ratio:.2%}"))

# Display the reference image permanently from book
ref_image = Image.open("reftable.png")
ref_image = ref_image.resize((600, 300), Image.LANCZOS)  # Resize to fit the GUI
img = ImageTk.PhotoImage(ref_image)

img_label = tk.Label(root, image=img)
img_label.image = img  # Keep a reference to avoid garbage collection
img_label.pack(pady=10)


load_button = tk.Button(root, text="Load CSV File", command=load_file)
load_button.pack(pady=10)

run_button = tk.Button(root, text="Run Data Quality Checks", command=run_checks)
run_button.pack(pady=10)

# Table display results
columns = ("Check", "Result")
result_table = ttk.Treeview(root, columns=columns, show="headings", height=15)
result_table.heading("Check", text="Data Quality Check")
result_table.heading("Result", text="Result")
result_table.pack(pady=20)

# Start Tkinter 
root.mainloop()
