# Project 3 — Q&A Session Notes (Coach: Daniel)

Summary of questions and answers from the class Q&A session for anyone who missed it.

---

## Data Sources

**Q: Do we need to use exactly the listed data sources?**
A: No, they are suggested datasets. You can use any combination. You can shift to a different country or go global. Any combination of sources that can be joined is fine.

**Q: Is it US-only or can we do global analysis?**
A: Global is fine. If you want COVID numbers by country using WHO data, that's perfectly okay.

**Q: Do we need APIs that require authentication?**
A: Doesn't matter. Use whatever you want — authenticated or not.

**Q: Can we use CSV downloads from CDC instead of the API?**
A: Yes, but if you're getting CSVs, you need an automated way to keep getting those CSVs. Python should automatically grab the latest data.

**Q: Does the data need to be ongoing and current?**
A: Yes, it needs to be updatable. But whatever's as current as you can get is fine. COVID data isn't updated as frequently anymore — someone looked into it and ended up doing Flu data instead because it updated weekly.

**Q: Are there daily COVID averages available?**
A: Probably not anymore. Most data is now done differently (weekly). You might have to go to another country (international sources) to get daily metrics. Data should cover at least the last 3 years.

---

## Architecture & Tech Stack

**Q: Do we need Docker for Airflow?**
A: No. Airflow runs in a virtual environment (like the previous Airflow project). You can use `uv` for the virtual environment. No Docker needed.

**Q: How does the architecture connect?**
A: dbt talks to Snowflake. Airflow triggers dbt. The pipeline should be autonomous — "I created this pipeline, I dumped it off to the cloud, and it's running on its own. It got a job and left the house, and I never see it."

**Q: How many schemas do we need in Snowflake?**
A: The documentation suggests RAW, STAGING, INTERMEDIATE, and MARTS (4 schemas). But you can use either schemas or tables or some way to logically separate the data into those pieces.

**Q: For Snowflake, do we use a shared environment?**
A: No. You log in through your personal Snowflake accounts. Create a user in Snowflake, put that user in dbt, and dbt does the things in Snowflake.

---

## Metrics

**Q: What does "7-day rolling average of new cases" mean?**
A: It's a SQL window function over each 7-day period. In the dashboard, if someone picks a date range, you calculate the average for those days.

**Q: What is "data freshness by source"?**
A: A report on how stale or fresh each data source is — when was the last time data was updated/ingested.

---

## Streamlit Dashboard

**Q: Is there a specific reason for Streamlit?**
A: It's just for presenting the data. It's easier and more user-friendly than Metabase or similar tools. It connects directly to Snowflake.

**Q: Who can help with Streamlit?**
A: Alex is the resident expert on Streamlit (he's teaching evening class but still available). Also, Claude (AI) is good at Streamlit.

---

## Project Logistics

**Q: What's the timeline?**
A: Two weeks — all of this week and all of next week. About 6 class days. Presentation likely a week from Saturday.

**Q: How long is the presentation?**
A: 20-25 minutes per team (as stated in the doc). Past presentations have been 10-20 minutes. For capstones it'll be 15 minutes, so aim for that as a benchmark.

**Q: Where do we set up the repo?**
A: Create your own repos, set them up, configure them, push them to the NSS Data Engineering October cohort GitHub. Create a repo and add your collaborator.

**Q: Will there be changes to requirements mid-project?**
A: Yes. "There's gonna be some twists in this project. They will come during the project. Because in the real world, stakeholders think they know what they want, and then they come back and change little pieces of things." Be prepared to adapt.

---

## Key Takeaways

1. **Minimum 2 data sources** that can be joined
2. **Pipeline must be automated** — "If you're getting CSVs, you have to have some automated way to keep getting those CSVs." / "I created this pipeline, I dumped it off to the cloud, and it's running on its own."
3. **Airflow orchestrates everything** (runs in venv, no Docker)
4. **dbt connects to Snowflake**, Airflow triggers dbt
5. **Streamlit dashboard** connects to Snowflake for visualization
6. **COVID data may be stale** — consider alternatives (Flu, international sources) or accept weekly granularity
7. **Expect requirement changes** mid-project (simulating real stakeholders)
8. **Presentation ~15-20 minutes** with live demo
