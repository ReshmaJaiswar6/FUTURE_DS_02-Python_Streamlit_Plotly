import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("Merged_SaaS_Subs_cleaned_datta.csv")

# Basic cleaning
df['signup_date'] = pd.to_datetime(df['signup_date'])
df['churn_date'] = pd.to_datetime(df['churn_date'])

# ---- KPIs ----
st.title("📊 SaaS Customer Churn Dashboard")

col1, col2, col3, col4 = st.columns(4)

churn_rate = round(df['is_churned'].mean() * 100, 2)
avg_tenure = int(df['tenure_days'].mean())
total_users = len(df)
revenue_loss = int(df[df['is_churned'] == 1]['mrr_amount'].sum())

col1.metric("Churn Rate", f"{churn_rate}%")
col2.metric("Avg Tenure (Days)", avg_tenure)
col3.metric("Total Users", total_users)
col4.metric("Revenue Lost", f"${revenue_loss}")

st.markdown("---")

# ---- Churn by Plan ----
st.subheader("Churn Rate by Plan")

plan_churn = df.groupby('plan_tier_x')['is_churned'].mean().reset_index()
plan_churn['is_churned'] *= 100

fig1 = px.bar(
    plan_churn,
    x='plan_tier_x',
    y='is_churned',
    text='is_churned',
    labels={'is_churned': 'Churn %', 'plan_tier_x': 'Plan'},
)

st.plotly_chart(fig1, use_container_width=True)

# ---- Risk Segmentation ----
st.subheader("Customer Risk Segmentation")

fig2 = px.scatter(
    df,
    x='usage_count',
    y='ticket_count',
    color='is_churned',
    hover_data=['plan_tier_x'],
)

st.plotly_chart(fig2, use_container_width=True)

# ---- Tenure Distribution ----
st.subheader("When Customers Churn")

fig3 = px.histogram(
    df[df['is_churned'] == 1],
    x='tenure_days',
    nbins=30,
)

st.plotly_chart(fig3, use_container_width=True)

# ---- Revenue Loss ----
st.subheader("Revenue Loss by Plan")

rev_loss = df[df['is_churned'] == 1].groupby('plan_tier_x')['mrr_amount'].sum().reset_index()

fig4 = px.bar(
    rev_loss,
    x='plan_tier_x',
    y='mrr_amount',
    text='mrr_amount',
)

st.plotly_chart(fig4, use_container_width=True)

# ---- Insights ----
st.markdown("---")
st.subheader("Key Insights")

st.write("- High churn linked to low usage and high support tickets")
st.write("- Certain plans contribute more to revenue loss")
st.write("- Most churn happens early in customer lifecycle")

st.subheader("Recommended Actions")

st.write("- Target low-usage users with onboarding nudges")
st.write("- Improve support response for high-ticket users")
st.write("- Focus retention efforts in early tenure phase")
