# CrewAI Full-Stack Application Generator

This project uses a CrewAI-powered team of agents to automate the design, implementation, and containerization of a full-stack web application based on an initial data analysis report from Google BigQuery.

## Prerequisites

1.  **Python 3.10+**: Ensure you have a modern version of Python installed.
2.  **Poetry**: This project uses Poetry for dependency management. If you don't have it, you can install it following the official documentation.
3.  **Google Cloud SDK (`gcloud`)**: You must have the `gcloud` CLI installed and authenticated to a Google Cloud project with the BigQuery API enabled.
    - [Install gcloud](https://cloud.google.com/sdk/docs/install)
    - Run `gcloud auth application-default login` to authenticate.

## Setup Instructions

1.  **Clone the Repository**:
    ```bash
    git clone <repository_url>
    cd cag/me
    ```

2.  **Install Dependencies**:
    Use Poetry to create a virtual environment and install all required packages.
    ```bash
    poetry install
    ```

3.  **Activate the Virtual Environment**:
    All subsequent commands should be run from within the virtual environment.
    ```bash
    poetry shell
    ```

## How to Run the Application

The main entrypoint for the application is `src/me/main.py`. This script will kick off the entire 6-step agentic workflow. **Do not use `crewai run`**, as it will not work with this project's custom setup.

**To run the full process:**

Execute the `main.py` script from the project root (`cag/me`):
```bash
python src/me/main.py
```

### The Workflow Steps:

1.  **Analysis (`bq_expert`)**: The crew starts by querying BigQuery to generate a data analysis report. The output is saved to a new directory under `job_runs/`.
2.  **Full-Stack Design (`software_architect`)**: The architect designs the application's backend, frontend, and containerization strategy based on the report.
3.  **Backend Implementation (`polyglot_developer`)**: The developer writes the FastAPI server and its `Dockerfile`.
4.  **Frontend Implementation (`ui_ux_designer`)**: The designer creates the API-driven frontend and its `Dockerfile`.
5.  **Containerization (`software_architect`)**: The architect creates a `docker-compose.yml` file to run the application.
6.  **Review (`customer_chatbot`)**: The final application is reviewed for correctness and alignment with the initial goals.

### Interactive Mode

After the main workflow is complete, the application will enter an interactive mode. You can ask questions or provide feedback directly to the "Cloud Software and DevOps Architect" to refine the generated application.

To exit the interactive mode, type `exit` or `quit`.
