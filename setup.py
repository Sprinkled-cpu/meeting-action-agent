from setuptools import setup, find_packages

setup(
    name="meeting-action-agent",
    version="1.0.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pydantic>=2.7.0",
        "fastapi>=0.110.0",
        "uvicorn>=0.29.0",
        "httpx>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "meeting-action=meeting_action_agent.cli:main",
        ],
    },
)
