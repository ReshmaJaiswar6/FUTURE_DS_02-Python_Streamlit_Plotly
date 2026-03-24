import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# Load data
df = pd.read_csv("Merged_SaaS_Subs_cleaned_data.csv")

# Basic cleaning
df['signup_date'] = pd.to_datetime(df['signup_date'])
df['churn_date'] = pd.to_datetime(df['churn_date'])

# ---- KPIs ----
st.title("SaaS Susbcribtion Customer Churn & Retention Insights")

st.subheader("Overall Business Performance")
st.caption("Churn is a key driver of revenue and customer retention.")
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

#--------Customer Drop-off Analysis--------
st.subheader("Customer Drop-off Analysis")
st.caption("Significant user loss occurs after initial engagement.")

st.warning("Drop-off increases sharply after initial engagement → onboarding gap")



stages = {
    "Total Users": len(df),
    "Active Users": len(df[df['is_churned'] == 0]),
    "Engaged Users": len(df[df['usage_count'] > df['usage_count'].median()]),
    "Retained Users": len(df[df['is_churned'] == 0])
}

funnel_df = pd.DataFrame(list(stages.items()), columns=['Stage', 'Users'])

fig = px.bar(funnel_df, x='Stage', y='Users', text='Users')
st.plotly_chart(fig, use_container_width=True)

st.caption("Drop-off increases sharply after initial engagement → onboarding gap")


# --------Churn by Plan Tier---------
st.subheader("Churn by Plan Tier")
st.caption("Churn rates vary across subscription plans.")
st.warning("Certain plans show significantly higher churn risk")

plan_churn = df.groupby('plan_tier_x')['is_churned'].mean() * 100
plan_churn = plan_churn.reset_index()

fig = px.bar(
    plan_churn,
    x='is_churned',
    y='plan_tier_x',
    orientation='h',
    text='is_churned',
    color = 'plan_tier_x'
)

st.plotly_chart(fig, use_container_width=True)



#  -------Customer Risk Segmentation-------------
st.subheader("Customer Risk Segmentation")
st.caption("Low engagement and high support needs indicate churn risk.")
st.warning("Low usage + high support tickets = highest churn risk")

fig = px.scatter(
    df,
    x='usage_count',
    y='ticket_count',
    color='is_churned',
    opacity=0.6
)

fig.add_vline(x=df['usage_count'].median(), line_dash="dash")
fig.add_hline(y=df['ticket_count'].median(), line_dash="dash")

st.plotly_chart(fig, use_container_width=True)



#  -----------Churn Timing Analysis------------

st.subheader("Churn Timing Analysis")
st.caption("Customers are most likely to churn early in their lifecycle.")
st.warning("Most churn happens early in the lifecycle")

fig = px.histogram(
    df[df['is_churned'] == 1],
    x='tenure_days',
    nbins=30
)

st.plotly_chart(fig, use_container_width=True)

#-------Revenue Impact of Churn-------
st.subheader("Revenue Impact of Churn")
st.caption("Revenue loss is concentrated in specific customer segments.")
st.warning("Revenue loss concentrated in specific plans")

revenue_loss = df[df['is_churned'] == 1].groupby('plan_tier_x')['mrr_amount'].sum().reset_index()

fig = px.bar(
    revenue_loss,
    x='mrr_amount',
    y='plan_tier_x',
    orientation='h',
    text='mrr_amount',
    color = ' plan_tier_x'
)

st.plotly_chart(fig, use_container_width=True)

#--------
st.subheader("Key Insights")

st.write("- High churn linked to low usage and high support tickets")
st.write("- Certain plans contribute more to revenue loss")
st.write("- Most churn happens early in customer lifecycle")

st.subheader("Recommended Actions")

st.write("- Target low-usage users with onboarding nudges")
st.write("- Improve support response for high-ticket users")
st.write("- Focus retention efforts in early tenure phase")
#---------------
st.markdown("---")
st.subheader("Final Dataset (Merged & Cleaned)")
if st.checkbox("Show Dataset"):
    st.dataframe(df, use_container_width=True)



