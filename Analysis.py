

# 1. Imports
# 2. Data Loading
# 3. Data Processing
# 4. Feature Engineering
# 5. Analysis
# 6. Visualization
# 7. Business Insights

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#1
def load_data():
    accounts = pd.read_csv('ravenstack_accounts.csv')
    subscriptions = pd.read_csv('ravenstack_subscriptions.csv')
    usage = pd.read_csv('ravenstack_feature_usage.csv')
    tickets = pd.read_csv('ravenstack_support_tickets.csv')
    churn = pd.read_csv('ravenstack_churn_events.csv')
    return accounts, subscriptions, usage, tickets, churn

#2 Data Merge Function
def create_master_dataset(accounts, subscriptions, churn, usage, tickets):
    df = accounts.merge(subscriptions, on='account_id', how='left')
    df = df.merge(churn, on='account_id', how='left')

    usage_map = usage.merge(
        subscriptions[['subscription_id', 'account_id']],
        on='subscription_id', how='left'
    )

    usage_summary = usage_map.groupby('account_id')['usage_count'].sum().reset_index()
    ticket_summary = tickets.groupby('account_id').size().reset_index(name='ticket_count')

    df = df.merge(usage_summary, on='account_id', how='left')
    df = df.merge(ticket_summary, on='account_id', how='left')

    df['ticket_count'] = df['ticket_count'].fillna(0)
    df['is_churned'] = df['churn_date'].notnull().astype(int)

    return df

#3
def prepare_analysis_df(df):
    df = df.sort_values('signup_date') \
           .drop_duplicates('account_id', keep='last') \
           .copy()

    df['signup_date'] = pd.to_datetime(df['signup_date'])
    df['churn_date'] = pd.to_datetime(df['churn_date'])

    reference_date = df['signup_date'].max()
    df['tenure_days'] = (
        df['churn_date'].fillna(reference_date) - df['signup_date']
    ).dt.days

    return df

# Call the data loading and processing functions to create clean_df
accounts, subscriptions, usage, tickets, churn = load_data()
master_df = create_master_dataset(accounts, subscriptions, churn, usage, tickets)
clean_df = prepare_analysis_df(master_df)

# Now save the clean_df to CSV
clean_df.to_csv('Merged_SaaS_Subs_cleaned_data.csv', index=False)
print("DataFrame 'clean_df' saved to 'Merged_SaaS_Subs_cleaned_data.csv'")

#4. Analysis Functions

def calculate_churn(df):
    churn_rate = df['is_churned'].mean() * 100
    print(f"Churn Rate: {churn_rate:.2f}%")

calculate_churn(clean_df)

df = clean_df
stages = {
        "Total Users": len(df),
        "Active Users": len(df[df['usage_count'] > 0]),
        "Engaged Users": len(df[df['usage_count'] > df['usage_count'].median()]),
        "Retained Users": len(df[df['is_churned'] == 0])}
plt.figure()
plt.bar(stages.keys(), stages.values())
plt.title("Customer Funnel: Drop-off Analysis")
plt.xticks(rotation=30)
plt.ylabel("Users")
plt.show()

#SEGMENTATION: Who is likely to churn? (By Plan Tier)

plan_analysis = clean_df.groupby('plan_tier_x')['is_churned'].mean() * 100
print(f"\n--- Segmentation by Plan ---")
print(plan_analysis.sort_values(ascending=False))

# Calculate Churn % by Plan
plan_churn = clean_df.groupby('plan_tier_x')['is_churned'].mean() * 100

# Plot simple Bar Chart
ax = plan_churn.plot(kind='barh', color=['skyblue', 'salmon', 'lightgreen'])
plt.title("Churn Rate % by Plan Tier")
plt.xlabel("Churn %")
plt.ylabel("Plan Tier")

# Add labels to the bars
for container in ax.containers:
    ax.bar_label(container, fmt='%.2f%%')

plt.show()

# CUSTOMER RISK SEGMENTATION
plt.figure()

sns.scatterplot(
    data=df,
    x='usage_count',
    y='ticket_count',
    hue='is_churned',
    alpha=0.6
)

# Add median lines (decision boundaries)
plt.axvline(df['usage_count'].median(), linestyle='--')
plt.axhline(df['ticket_count'].median(), linestyle='--')

plt.title("High Ticket + Low Usage Users Are High Risk")

plt.show()
print(f"Recommendation: Contact users with usage below {df['usage_count'].median()}")

# CUSTOMER LIFETIME PATTERNS: How long do they stay?
# Convert dates and calculate Tenure in days
df['signup_date'] = pd.to_datetime(df['signup_date'])
df['churn_date'] = pd.to_datetime(df['churn_date'])

# Using the max date in the dataset as a reference for active users
reference_date = df['signup_date'].max()
df['tenure_days'] = (df['churn_date'].fillna(reference_date) - df['signup_date']).dt.days

# Calculate tenure specifically for churned customers
churned_tenure = df[df['is_churned'] == 1]['tenure_days']

print(f"\n---Lifetime Patterns ---")
print(f"Average Tenure Until Churn: {churned_tenure.mean():.1f} days")
print(f"Median Tenure Until Churn: {churned_tenure.median():.1f} days")

# Plot the distribution of how long people stay
sns.histplot(data=df[df['is_churned']==1], x='tenure_days', color='red', kde=True)
plt.title("When do most people churn? (Day Distribution)")

print("Most Users Churn Within Early Lifecycle")
print(f"Median Days until Churn: {df[clean_df['is_churned']==1]['tenure_days'].median()}")

plt.xlabel("Days until cancellation")
plt.show()

# REVENUE LOSS BY PLAN
revenue_loss = df[df['is_churned'] == 1].groupby('plan_tier_x')['mrr_amount'].sum()

plt.figure()
ax = revenue_loss.plot(kind='barh')

plt.title("Revenue Loss is Highest in Specific Plans")
plt.xlabel("Revenue Lost ($)")
plt.ylabel("Plan Tier")
# Add labels to the bars
for container in ax.containers:
    ax.bar_label(container, fmt='$%.1f')

plt.show()

# PLAN DISTRIBUTION + CHURN
cross_tab = pd.crosstab(df['plan_tier_x'], df['is_churned'])

ax = cross_tab.plot(kind='barh', stacked=True)

plt.title("Customer Distribution by Plan and Churn")
plt.xlabel("Number of Customers")
plt.ylabel("Plan Tier")
# Add labels to the bars
for container in ax.containers:
    ax.bar_label(container, fmt='%d')

plt.show()
