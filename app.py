import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Bike Rentals Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("train.csv")

    # Convert datetime
    df["datetime"] = pd.to_datetime(df["datetime"])

    # New time columns
    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["dayofweek"] = df["datetime"].dt.dayofweek
    df["hour"] = df["datetime"].dt.hour

    # Season names
    season_map = {1: "spring", 2: "summer", 3: "fall", 4: "winter"}
    df["season_name"] = df["season"].map(season_map)

    # Day period
    def get_period(h):
        if 0 <= h < 6:
            return "night"
        elif 6 <= h < 12:
            return "morning"
        elif 12 <= h < 18:
            return "afternoon"
        else:
            return "evening"

    df["dayperiod"] = df["hour"].apply(get_period)

    return df

df = load_data()

# Sidebar filters (3 interactive widgets)
st.sidebar.header("Filters")

years = sorted(df["year"].unique())
selected_years = st.sidebar.multiselect(
    "Select year(s)",
    options=years,
    default=years,
)

seasons = sorted(df["season_name"].unique())
selected_seasons = st.sidebar.multiselect(
    "Select season(s)",
    options=seasons,
    default=seasons,
)

workingday_option = st.sidebar.radio(
    "Working day filter",
    options=["All", "Working days", "Non-working days"],
    index=0,
)

# Apply filters
filtered_df = df[df["year"].isin(selected_years)]
filtered_df = filtered_df[filtered_df["season_name"].isin(selected_seasons)]

if workingday_option == "Working days":
    filtered_df = filtered_df[filtered_df["workingday"] == 1]
elif workingday_option == "Non-working days":
    filtered_df = filtered_df[filtered_df["workingday"] == 0]


st.title("Washington D.C. Bike Rentals Dashboard")
st.write("Interactive summary of bike rentals (Assignments I & II).")

# Key metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total rentals", f"{filtered_df['count'].sum():,}")
col2.metric("Avg hourly rentals", f"{filtered_df['count'].mean():.0f}")
col3.metric("Peak hour", f"{filtered_df.groupby('hour')['count'].mean().idxmax()}:00")
col4.metric("Records", f"{len(filtered_df):,}")


# Plot 1: Mean rentals by month
st.subheader("📊 Mean rentals by month")
monthly = (
    filtered_df.groupby("month")["count"]
    .mean()
    .reset_index()
    .sort_values("month")
)
fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(data=monthly, x="month", y="count", ax=ax1, color="skyblue")
ax1.set_xlabel("Month")
ax1.set_ylabel("Mean hourly rentals")
ax1.set_title("Rentals by month")
st.pyplot(fig1)

# Plot 2: Rentals by hour of day
st.subheader("🕐 Rentals by hour of day")
hourly = (
    filtered_df.groupby("hour")["count"]
    .mean()
    .reset_index()
)
fig2, ax2 = plt.subplots(figsize=(10, 5))
sns.lineplot(data=hourly, x="hour", y="count", ax=ax2, marker="o", color="green")
ax2.set_xlabel("Hour of day")
ax2.set_ylabel("Mean hourly rentals")
ax2.set_title("Peak hours")
st.pyplot(fig2)

# Plot 3: Rentals by weather
st.subheader("🌤️ Rentals by weather")
weather_means = (
    filtered_df.groupby("weather")["count"]
    .agg(["mean", "std", "count"])
    .reset_index()
)
weather_means["ci_low"] = weather_means["mean"] - 1.96 * (weather_means["std"] / weather_means["count"].apply(lambda x: x**0.5))
weather_means["ci_high"] = weather_means["mean"] + 1.96 * (weather_means["std"] / weather_means["count"].apply(lambda x: x**0.5))

fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.errorbar(weather_means["weather"], weather_means["mean"], 
             yerr=[weather_means["mean"] - weather_means["ci_low"], 
                   weather_means["ci_high"] - weather_means["mean"]],
             fmt="o-", capsize=5, color="orange")
ax3.set_xlabel("Weather (1=Clear, 2=Mist, 3=Light rain/snow, 4=Heavy)")
ax3.set_ylabel("Mean hourly rentals")
ax3.set_title("Rentals by weather (with 95% CI)")
st.pyplot(fig3)

# Plot 4: Dayperiod vs working day
st.subheader("📅 Rentals by day period & working day")
pivot = pd.pivot_table(
    filtered_df, 
    values="count", 
    index="dayperiod", 
    columns="workingday", 
    aggfunc="mean"
)
fig4, ax4 = plt.subplots(figsize=(10, 5))
pivot.plot(kind="bar", ax=ax4)
ax4.set_xlabel("Day period")
ax4.set_ylabel("Mean hourly rentals")
ax4.set_title("Rentals by day period (0=non-working, 1=working)")
ax4.legend(title="Working day")
st.pyplot(fig4)

# Plot 5: Correlation heatmap
st.subheader("🔗 Correlation heatmap")
numeric_cols = filtered_df.select_dtypes(include=['int64', 'float64']).columns
corr = filtered_df[numeric_cols].corr()
fig5, ax5 = plt.subplots(figsize=(12, 8))
sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax5)
ax5.set_title("Correlation matrix (shows registered, hour, temp strongest with count)")
st.pyplot(fig5)


#df = load_data()

# Sidebar filters ← NEW
...

#st.title("...")
# #st.write("...")

# Plot 1 ← NEW
...
