import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Data Analysis Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# HEADER
# =========================================================

st.title("📊 AI-Powered Sales Data Analysis Dashboard")
st.caption(
    "Interactive business intelligence dashboard built with Python, "
    "Pandas, Plotly and Streamlit"
)

st.divider()

# =========================================================
# FILE UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "📂 Upload your sales CSV file",
    type=["csv"]
)

# Stop application if no file is uploaded
if uploaded_file is None:
    st.info("👆 Upload a CSV file to start analyzing your data.")
    st.stop()

# =========================================================
# LOAD DATA
# =========================================================

try:
    df = pd.read_csv(uploaded_file)

except Exception as e:
    st.error(f"❌ Error reading the CSV file: {e}")
    st.stop()

# =========================================================
# CHECK REQUIRED COLUMNS
# =========================================================

required_columns = [
    "Date",
    "Product",
    "Category",
    "Region",
    "Sales",
    "Quantity",
    "Profit"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "❌ Your CSV file is missing the following required columns:"
    )

    st.write(missing_columns)

    st.info(
        "Required columns: Date, Product, Category, Region, "
        "Sales, Quantity and Profit."
    )

    st.stop()

# =========================================================
# DATA TYPE CONVERSION
# =========================================================

# Convert Date column
df["Date"] = pd.to_datetime(
    df["Date"],
    dayfirst=True,
    errors="coerce"
)

# Convert numerical columns
numeric_columns = [
    "Sales",
    "Quantity",
    "Profit"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# =========================================================
# DATA QUALITY CHECK
# =========================================================

invalid_dates = df["Date"].isna().sum()

if invalid_dates > 0:

    st.warning(
        f"⚠️ {invalid_dates} invalid date(s) were found."
    )

# Remove rows with invalid essential data
df = df.dropna(
    subset=[
        "Date",
        "Sales",
        "Quantity",
        "Profit"
    ]
)

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Dashboard Filters")

filtered_df = df.copy()

# ---------------- REGION FILTER ----------------

regions = sorted(
    df["Region"].dropna().unique()
)

selected_regions = st.sidebar.multiselect(
    "🌎 Select Region",
    options=regions,
    default=regions
)

if selected_regions:

    filtered_df = filtered_df[
        filtered_df["Region"].isin(selected_regions)
    ]

# ---------------- CATEGORY FILTER ----------------

categories = sorted(
    df["Category"].dropna().unique()
)

selected_categories = st.sidebar.multiselect(
    "🛍️ Select Category",
    options=categories,
    default=categories
)

if selected_categories:

    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]

# =========================================================
# DATE FILTER
# =========================================================

st.sidebar.subheader("📅 Date Range")

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.sidebar.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = filtered_df[
        (filtered_df["Date"].dt.date >= start_date)
        &
        (filtered_df["Date"].dt.date <= end_date)
    ]

# =========================================================
# CHECK FILTER RESULT
# =========================================================

if filtered_df.empty:

    st.warning(
        "⚠️ No data matches the selected filters."
    )

    st.stop()

# =========================================================
# BUSINESS OVERVIEW
# =========================================================

st.header("📈 Business Overview")

# KPI calculations

total_sales = filtered_df["Sales"].sum()

total_profit = filtered_df["Profit"].sum()

total_quantity = filtered_df["Quantity"].sum()

total_orders = len(filtered_df)

profit_margin = (
    total_profit / total_sales * 100
    if total_sales > 0
    else 0
)

average_order_value = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)

# =========================================================
# KPI CARDS
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "💰 Total Sales",
        f"₹{total_sales:,.0f}"
    )

with col2:

    st.metric(
        "💵 Total Profit",
        f"₹{total_profit:,.0f}"
    )

with col3:

    st.metric(
        "📦 Quantity Sold",
        f"{total_quantity:,}"
    )

with col4:

    st.metric(
        "🧾 Orders",
        f"{total_orders:,}"
    )

# Second KPI row

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "📊 Profit Margin",
        f"{profit_margin:.2f}%"
    )

with col2:

    st.metric(
        "🛒 Average Order Value",
        f"₹{average_order_value:,.0f}"
    )

st.divider()

# =========================================================
# SALES BY REGION
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🌎 Sales by Region")

    region_sales = (
        filtered_df
        .groupby("Region")["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig_region = px.bar(
        region_sales,
        x="Region",
        y="Sales",
        title="Sales by Region",
        text_auto=True
    )

    fig_region.update_layout(
        xaxis_title="Region",
        yaxis_title="Sales (₹)"
    )

    st.plotly_chart(
        fig_region,
        use_container_width=True
    )

# =========================================================
# SALES BY CATEGORY
# =========================================================

with col2:

    st.subheader("🛍️ Sales by Category")

    category_sales = (
        filtered_df
        .groupby("Category")["Sales"]
        .sum()
        .reset_index()
        .sort_values(
            "Sales",
            ascending=False
        )
    )

    fig_category = px.pie(
        category_sales,
        names="Category",
        values="Sales",
        title="Sales Distribution by Category"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )

# =========================================================
# MONTHLY SALES TREND
# =========================================================

st.subheader("📅 Monthly Sales Trend")

monthly_sales = (
    filtered_df
    .set_index("Date")
    .resample("ME")["Sales"]
    .sum()
    .reset_index()
)

fig_monthly = px.line(
    monthly_sales,
    x="Date",
    y="Sales",
    markers=True,
    title="Monthly Sales Performance"
)

fig_monthly.update_layout(
    xaxis_title="Month",
    yaxis_title="Sales (₹)"
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)

# =========================================================
# SALES VS PROFIT
# =========================================================

st.subheader("💰 Sales vs Profit by Product")

sales_profit = (
    filtered_df
    .groupby("Product")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum")
    )
    .reset_index()
    .sort_values(
        "Sales",
        ascending=False
    )
)

fig_sales_profit = px.bar(
    sales_profit,
    x="Product",
    y=["Sales", "Profit"],
    barmode="group",
    title="Sales vs Profit by Product"
)

fig_sales_profit.update_layout(
    xaxis_title="Product",
    yaxis_title="Amount (₹)"
)

st.plotly_chart(
    fig_sales_profit,
    use_container_width=True
)

# =========================================================
# PRODUCT PERFORMANCE
# =========================================================

st.subheader("🏆 Product Performance")

product_sales = (
    filtered_df
    .groupby("Product")
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum")
    )
    .reset_index()
    .sort_values(
        "Sales",
        ascending=False
    )
)

st.dataframe(
    product_sales,
    use_container_width=True,
    hide_index=True
)

# =========================================================
# TOP 5 PRODUCTS
# =========================================================

st.subheader("🔥 Top 5 Products by Sales")

top_products = product_sales.head(5)

fig_products = px.bar(
    top_products,
    x="Product",
    y="Sales",
    text_auto=True,
    title="Top 5 Products by Sales"
)

fig_products.update_layout(
    xaxis_title="Product",
    yaxis_title="Sales (₹)"
)

st.plotly_chart(
    fig_products,
    use_container_width=True
)

# =========================================================
# AUTOMATED BUSINESS INTELLIGENCE
# =========================================================

st.header("🤖 Automated Business Intelligence")

# Best region

region_profit = (
    filtered_df
    .groupby("Region")["Profit"]
    .sum()
    .sort_values(ascending=False)
)

best_profit_region = region_profit.index[0]

best_profit_region_value = region_profit.iloc[0]

# Best sales region

best_sales_region = (
    filtered_df
    .groupby("Region")["Sales"]
    .sum()
    .idxmax()
)

best_sales_region_value = (
    filtered_df
    .groupby("Region")["Sales"]
    .sum()
    .max()
)

# Best product

best_product = (
    filtered_df
    .groupby("Product")["Sales"]
    .sum()
    .idxmax()
)

best_product_sales = (
    filtered_df
    .groupby("Product")["Sales"]
    .sum()
    .max()
)

# Best category

best_category = (
    filtered_df
    .groupby("Category")["Sales"]
    .sum()
    .idxmax()
)

best_category_sales = (
    filtered_df
    .groupby("Category")["Sales"]
    .sum()
    .max()
)

# =========================================================
# INSIGHT CARDS
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.success(
        f"📍 **Top Sales Region**\n\n"
        f"{best_sales_region}\n\n"
        f"₹{best_sales_region_value:,.0f}"
    )

with col2:

    st.info(
        f"🏆 **Best-Selling Product**\n\n"
        f"{best_product}\n\n"
        f"₹{best_product_sales:,.0f}"
    )

with col3:

    st.warning(
        f"📦 **Top Category**\n\n"
        f"{best_category}\n\n"
        f"₹{best_category_sales:,.0f}"
    )

# =========================================================
# PROFIT INSIGHT
# =========================================================

st.subheader("💡 Profit Analysis")

st.write(
    f"💰 **{best_profit_region}** generated the highest total profit "
    f"of **₹{best_profit_region_value:,.0f}**."
)

if profit_margin >= 20:

    st.success(
        f"📈 The current profit margin is "
        f"**{profit_margin:.2f}%**, indicating strong profitability."
    )

elif profit_margin >= 10:

    st.info(
        f"📊 The current profit margin is "
        f"**{profit_margin:.2f}%**, indicating moderate profitability."
    )

else:

    st.warning(
        f"⚠️ The current profit margin is "
        f"**{profit_margin:.2f}%**. Consider reviewing costs "
        f"and pricing strategies."
    )

# =========================================================
# DATA QUALITY
# =========================================================

st.header("🧹 Data Quality")

missing_values = filtered_df.isnull().sum().sum()

duplicate_rows = filtered_df.duplicated().sum()

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Missing Values",
        missing_values
    )

with col2:

    st.metric(
        "Duplicate Rows",
        duplicate_rows
    )

with col3:

    st.metric(
        "Valid Records",
        len(filtered_df)
    )

# =========================================================
# DATASET INFORMATION
# =========================================================

st.header("📋 Dataset Information")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Rows",
        df.shape[0]
    )

with col2:

    st.metric(
        "Total Columns",
        df.shape[1]
    )

with col3:

    st.metric(
        "Filtered Rows",
        filtered_df.shape[0]
    )

# =========================================================
# RAW DATA
# =========================================================

with st.expander("🔍 View Raw Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Built with Python • Pandas • Plotly • Streamlit"
)