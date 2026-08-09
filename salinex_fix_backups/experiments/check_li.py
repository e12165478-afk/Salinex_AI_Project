import pandas as pd
import os

# مسیر فایل شما
file_path = r'C:\Users\Mirzaee\Desktop\Salinex_AI_Project\Combined_Real_Brine_Data_cleaned.csv'

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    
    # پیدا کردن ستونی که نام Li یا Lithium دارد
    li_column = [col for col in df.columns if 'Li' in col or 'lithium' in col.lower()]
    
    if li_column:
        col_name = li_column[0]
        print(f"--- تحلیل ستون: {col_name} ---")
        print(f"میانگین غلظت: {df[col_name].mean():.4f}")
        print(f"حداکثر غلظت: {df[col_name].max():.4f}")
        print(f"حداقل غلظت: {df[col_name].min():.4f}")
        print(f"تعداد ردیف‌ها: {len(df)}")
    else:
        print("ستونی با نام Lithium یا Li پیدا نشد. نام ستون‌های شما این‌ها هستند:")
        print(df.columns.tolist())
else:
    print("فایل پیدا نشد! مسیر را چک کنید.")