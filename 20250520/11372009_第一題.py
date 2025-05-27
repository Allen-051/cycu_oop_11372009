import pandas as pd

# 讀取 CSV 檔案
file_path = '20250520/example/midterm_scores.csv'
df = pd.read_csv(file_path)

# 計算每位學生低於 60 分的科目數量
subjects = ['Chinese', 'English', 'Math', 'History', 'Geography', 'Physics', 'Chemistry']
df['SubjectsBelow60'] = (df[subjects] < 60).sum(axis=1)

# 篩選超過 4 個科目（包含 4 科）低於 60 分的學生
low_subject_students = df[df['SubjectsBelow60'] >= 4]

# 將符合條件的學生及其科目分數輸出到新的 CSV 檔案
output_file_path = '20250520/example/low_subject_students_with_scores.csv'
low_subject_students.to_csv(output_file_path, index=False)

print("Students with 4 or more subjects below 60:")
print(low_subject_students[['Name', 'StudentID', 'SubjectsBelow60', *subjects]])

print(f"Results with scores have been saved to {output_file_path}")