from streamlit_tags import st_tags
import matplotlib.pyplot as plt
from history import History
import streamlit as st
import pandas as pd
import os


st.set_page_config(
    page_title = "AI-Senior-Assistant",
    page_icon = "✨",
    layout = "wide"
)

with st.sidebar:
    st.header(
        body="Statistics and History",
        divider="gray"
    )
    st.markdown("""
        **One of the tasks** of the application is to present the **performance** of the model used with the Ollama tool.
        When sending a query, the Ollama server returns additional **information** about the **time** required by the model.
        Just select the **date**, **type** and **metric** you want to check.
        
        **The second option** is to check whether a given activity was performed on the computer by **searching** the **vector database** of desktop screenshots based on the **description**.
    """)


# Create an object to fetch data from SqliteDB and ChromaDB
app_history = History()
df_sql = app_history.read_from_sqlite()

# To datetime and get the date
df_sql["created_at"] = pd.to_datetime(df_sql["created_at"])
df_sql["created_at_day"] = df_sql["created_at"].dt.date 

time_columns_dict = {
    "Total Duration" : "total_duration",
    "Load Duration"  : "load_duration",
    "Eval Duration"  : "eval_duration",
    "Prompt Eval Duration" : "prompt_eval_duration",
}

# Time measurements in ollama are saved in nanoseconds
for col in list(time_columns_dict.values()):
    df_sql[col] = df_sql[col].map(lambda x: x*10e-9) # Time to seconds

# Date range to date_input
min_date = df_sql["created_at"].dt.date.min()
max_date = df_sql["created_at"].dt.date.max()

# - The left column is used to display charts and statistics
# - The right column is used to get a screenshot of the activity history according to the description.
left_column, right_column = st.columns(2)
with left_column:
    st.header(
        body="🧠 LLM Performance Statistics",
        divider="blue"
    )
    
    date_input = st.date_input(
        label="🗓️ Choose a date",
        format="DD/MM/YYYY",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Select data based on type of request to Ollama
    types_list = st_tags(
        value=list(df_sql["type"].unique()),
        label="🏷️ Choose a type"
    )
    if types_list:
        df_sql = df_sql[df_sql["type"].isin(types_list)]
    
    # Select data based on the model
    models_list = st.selectbox(
        label="🧠 Choose a model",
        options=list(df_sql["model"].unique()),
    )
    if models_list:
        df_sql = df_sql[df_sql["model"] == models_list]

    # Select data based on the metrics you use
    metric = st.selectbox(
        label="📐 Choose a metric",
        options=list(time_columns_dict.keys())
    )

    chart_type = ""
    day_diff = 0
    if isinstance(date_input, tuple):
        # For 2 to 5 selected days, the chart is bar charts
        # For 1 and more than 5 days, the chart is line chart
        if len(date_input) == 2:
            chart_type = "bar"
            start_date, end_date = date_input
            filtered_df = df_sql[(df_sql["created_at"].dt.date >= start_date) & (df_sql["created_at"].dt.date <= end_date)]
            day_diff = (end_date - start_date).days

            df_grouped = filtered_df.groupby(["created_at_day", "type"])[time_columns_dict[metric]].agg(["mean", "std"]).reset_index()
            mean_pivot = df_grouped.pivot(index="created_at_day", columns="type", values="mean")
            std_pivot = df_grouped.pivot(index="created_at_day", columns="type", values="std")

        if len(date_input) == 1:
            chart_type = "line"
            filtered_df = df_sql[df_sql["created_at"].dt.date == date_input[0]]


    fig, ax = plt.subplots(figsize=(10, 5))
    if day_diff > 5:
        mean_pivot.plot(kind="line", yerr=std_pivot, capsize=5, ax=ax) # type: ignore

    elif chart_type == "bar":
        mean_pivot.plot(kind="bar", yerr=std_pivot, capsize=5, ax=ax) # type: ignore

    elif chart_type == "line":
        for data_type in filtered_df["type"].unique():              # type: ignore
            subset = filtered_df[filtered_df["type"] == data_type]  # type: ignore
            ax.plot(
                subset["created_at"],
                subset[time_columns_dict[metric]],
                marker="o",
                label=data_type
            )

    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Seconds", fontsize=12)
    ax.set_title("Performance statistics for the selected options", fontsize=14)
    ax.legend(title="Type", fontsize=10, loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.25)
    ax.tick_params("x", rotation=30)
    st.pyplot(fig)

    st.divider()

    ## Second chart - boxplot
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    df_sql.boxplot([time_columns_dict[metric]], by="created_at_day", ax=ax2)

    ax2.set_xlabel("Time", fontsize=12)
    ax2.set_ylabel("Seconds", fontsize=12)
    ax2.set_title("Performance statistics for the selected options", fontsize=14)
    ax2.tick_params("x", rotation=30)
    fig2.suptitle("")
    st.pyplot(fig2)



# Activity history
with right_column:
    st.header(
        body="⌛ Activity History",
        divider="blue"
    )

    # The left column is a text field for entering a description of the activity
    # The right column is a field for selecting the number of returned items
    sub_left_column, sub_right_column = st.columns(spec=[6, 1])
    with sub_left_column:
        text_search_input = st.text_input(
            label="🖼️ Describe the image"
        )
    with sub_right_column:
        n_results_input = st.number_input(
            label="✅ Select n-results",
            min_value=1,
            max_value=10
        )

    if st.button("Search", icon="🔍") and text_search_input:
        description, metadata = app_history.read_from_chroma(
            description=text_search_input, 
            n_results=n_results_input
        )
        
        for num_result in range(n_results_input):
            st.badge("New")
            st.markdown(fr"**Description:** `{description[0][num_result]}`")  # type: ignore
            st.markdown(fr"**Path:** `..\{os.path.basename(os.path.dirname(metadata[0][num_result]["img_path"]))}\{metadata[0][num_result]["filename"]}`")  # type: ignore
            st.markdown(fr"**Created at:** `{metadata[0][num_result]["created_at"]}`")  # type: ignore
            st.image(
                image=metadata[0][num_result]["img_path"],   # type: ignore
                caption=metadata[0][num_result]["filename"]  # type: ignore
            )
            st.divider()
        
