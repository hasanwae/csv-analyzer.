from flask import Flask, render_template, request
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
PLOT_FOLDER = "static/plots"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "No file part"
        
        file = request.files["file"]
        if file.filename == "":
            return "No selected file"
        
        if file and file.filename.endswith(".csv"):
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # قراءة البيانات
            df = pd.read_csv(filepath)

            # 🔹 تحليل وصفي
            shape = df.shape
            columns = df.dtypes.to_dict()
            missing = df.isnull().sum().to_dict()
            summary = df.describe(include="all").to_html(classes="table table-striped")
            preview = df.head().to_html(classes="table table-bordered")

            # 🔹 شرح وصفي نصي
            desc_text = []
            desc_text.append(f"الملف يحتوي على {shape[0]} صفوف و {shape[1]} أعمدة.")
            num_cols = df.select_dtypes(include='number').columns
            cat_cols = df.select_dtypes(exclude='number').columns
            desc_text.append(f"عدد الأعمدة الرقمية: {len(num_cols)} ({', '.join(num_cols) if len(num_cols)>0 else 'لا يوجد'}).")
            desc_text.append(f"عدد الأعمدة النصية/الفئوية: {len(cat_cols)} ({', '.join(cat_cols) if len(cat_cols)>0 else 'لا يوجد'}).")
            desc_text.append(f"أكثر عمود فيه قيم مفقودة: {max(missing, key=missing.get)} ({max(missing.values())} قيم مفقودة).")

            # 🔹 تنظيف مجلد الرسوم
            for f in os.listdir(PLOT_FOLDER):
                os.remove(os.path.join(PLOT_FOLDER, f))

            plots = []

            # Histogram للأعمدة الرقمية
            for col in num_cols[:2]:
                plt.figure(figsize=(6,4))
                sns.histplot(df[col].dropna(), kde=True, bins=30, color="skyblue")
                plt.title(f"Distribution of {col}")
                plot_path = os.path.join(PLOT_FOLDER, f"{col}_hist.png")
                plt.savefig(plot_path, bbox_inches="tight")
                plt.close()
                plots.append(f"plots/{col}_hist.png")

            # Boxplot لأعمدة رقمية
            for col in num_cols[:1]:
                plt.figure(figsize=(6,4))
                sns.boxplot(x=df[col], color="orange")
                plt.title(f"Boxplot of {col}")
                plot_path = os.path.join(PLOT_FOLDER, f"{col}_box.png")
                plt.savefig(plot_path, bbox_inches="tight")
                plt.close()
                plots.append(f"plots/{col}_box.png")

            # Heatmap للارتباط
            if len(num_cols) > 1:
                plt.figure(figsize=(6,4))
                corr = df[num_cols].corr()
                sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
                plt.title("Correlation Heatmap")
                plot_path = os.path.join(PLOT_FOLDER, "heatmap.png")
                plt.savefig(plot_path, bbox_inches="tight")
                plt.close()
                plots.append("plots/heatmap.png")

            # Bar chart للقيم النصية
            for col in cat_cols[:1]:
                plt.figure(figsize=(6,4))
                df[col].value_counts().nlargest(10).plot(kind="bar", color="green")
                plt.title(f"Top 10 categories in {col}")
                plot_path = os.path.join(PLOT_FOLDER, f"{col}_bar.png")
                plt.savefig(plot_path, bbox_inches="tight")
                plt.close()
                plots.append(f"plots/{col}_bar.png")

            return render_template("result.html", 
                                   shape=shape,
                                   columns=columns,
                                   missing=missing,
                                   summary=summary,
                                   preview=preview,
                                   desc_text=desc_text,
                                   plots=plots)
        else:
            return "Please upload a valid CSV file."
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
