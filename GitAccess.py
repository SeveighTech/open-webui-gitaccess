"""
title: GitAccess
author: ErrorRExorY/CptExorY, SeveighTech, Josetseph
author_url: https://pascal-frerks.de
git_url: https://github.com/WhyWaitServices/open-webui-gitaccess.git
description: This Tool allows the LLM to connect to one GitHub Repo to fetch its contents to ask it about it and use it to have your model always have the current state of the project
required_open_webui_version: 0.6.0
version: 0.2.0
licence: MIT
"""

from typing import Any, Optional, Callable, Awaitable, List, Dict
from pydantic import BaseModel, Field, ValidationError
import os
import requests
from datetime import datetime


class Filter:
    def __init__(self):
        pass

    def inlet(self, body: dict) -> dict:
        body["sanitized"] = "".join(e for e in body.get("input", "") if e.isalnum())
        return body

    def outlet(self, body: dict) -> dict:
        for message in body.get("messages", []):
            if message.get("role") == "assistant":
                message["content"] = f"**{message['content']}**"
        return body


class RepositoryPipe:
    class Valves(BaseModel):
        MODEL_ID: str = Field(default="github_repo")

    def __init__(self):
        self.valves = self.Valves()

    def pipe(self, body: dict) -> str:
        repo_url = body.get("repo_url", "")
        return f"Fetched content from {repo_url}"


class Action:
    def __init__(self):
        pass

    def create_action_button(self):
        return {
            "type": "button",
            "title": "Analyze Repo",
            "action": "analyze_repository",
        }


async def emit_citation(__event_emitter__, content, title, url):
    await __event_emitter__(
        {
            "type": "citation",
            "data": {
                "document": [content],
                "metadata": [
                    {"date_accessed": datetime.now().isoformat(), "source": title}
                ],
                "source": {"name": title, "url": url},
            },
        }
    )


class Tools:
    class Valves(BaseModel):
        access_token: str = Field(
            default=os.getenv("GITHUB_ACCESS_TOKEN", ""),
            description="GitHub Personal Access Token (needs repo access)",
            json_schema_extra={"secret": True},
        )
        owner: str = Field(
            default="",
            description="GitHub owner to access",
        )

    class UserValves(BaseModel):
        max_files: int = Field(
            default=20,
            description="Maximum number of files per directory (optional to limit)",
        )
        truncate_content: bool = Field(
            default=True,
            description="Truncate large files for better readability",
        )
        max_content_length: int = Field(
            default=5000,
            description="Maximum character length for file contents when truncation is enabled",
        )
        max_items: int = Field(
            default=5,
            description="Maximum number of issues, pull requests, etc. to retrieve per state (open/closed).",
        )
        max_comments: int = Field(
            default=5,
            description="Maximum number of comments to retrieve for issues and pull requests.",
        )

    def __init__(self):
        try:
            self.valves = self.Valves()
        except ValidationError as e:
            raise ValueError(f"Configuration error in Valves: {e}")
        self.user_valves = self.UserValves()
        self.filter = Filter()
        self.pipe = RepositoryPipe()
        self.action = Action()
        self.citation = False

    async def _fetch_directory_contents(
        self,
        api_url: str,
        headers: dict,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> Any:
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching contents from {api_url}...",
                        "done": False,
                        "hidden": False,
                    },
                }
            )
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            return f"Error fetching from {api_url}: {response.status_code} - {response.text}"
        items = response.json()
        result = []
        file_count = 0
        for item in items:
            if file_count >= self.user_valves.max_files:
                break
            if item["type"] == "dir":
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": f"Entering directory: {item['name']}...",
                                "done": False,
                            },
                        }
                    )
                sub_contents = await self._fetch_directory_contents(
                    item["url"], headers, __event_emitter__
                )
                result.append(
                    {
                        "name": item["name"],
                        "type": "dir",
                        "path": item["path"],
                        "contents": sub_contents,
                    }
                )
            elif item["type"] == "file":
                file_dict = {
                    "name": item["name"],
                    "type": "file",
                    "path": item["path"],
                }
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": f"Fetching file: {item['name']}...",
                                "done": False,
                            },
                        }
                    )
                if item.get("download_url"):
                    file_response = requests.get(item["download_url"])
                    if file_response.status_code == 200:
                        content = file_response.text
                        if (
                            self.user_valves.truncate_content
                            and len(content) > self.user_valves.max_content_length
                        ):
                            content = (
                                content[: self.user_valves.max_content_length] + "..."
                            )
                        file_dict["content"] = content
                    else:
                        file_dict["content_error"] = (
                            f"Error fetching file content: {file_response.status_code}"
                        )
                result.append(file_dict)
                file_count += 1
            else:
                result.append(
                    {
                        "name": item.get("name"),
                        "type": item.get("type"),
                        "path": item.get("path"),
                        "detail": item,
                    }
                )
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Finished fetching from {api_url}.",
                        "done": True,
                        "hidden": False,
                    },
                }
            )
        return result

    async def _fetch_github_data(
        self,
        api_url: str,
        headers: dict,
        data_type: str,
        max_items: int,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ) -> list:
        """Fetches data from the GitHub API and returns a list of dictionaries."""
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            if not isinstance(data, list):
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": f"No {data_type} found",
                                "done": True,
                                "hidden": False,
                            },
                        }
                    )
                return []
            # Limit the number of items
            limited_data = data[:max_items]
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Found {len(limited_data)} {data_type}",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return limited_data
        except requests.exceptions.RequestException as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error fetching {data_type}: {e}",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []

    async def fetch_repo_content(
        self,
        repo_name: str,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ):
        """Fetches the content of a specified repository within the configured owner.
        :param repo_name: The name of the repository to fetch.
        """
        owner = self.valves.owner
        if not self.valves.access_token or not owner:
            msg = "Access token or owner is not properly configured."
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "error", "data": {"description": msg, "done": True}}
                )
            return msg
        headers = {
            "Authorization": f"token {self.valves.access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        repo_url = f"{owner}/{repo_name}"
        repo_api_url = f"https://api.github.com/repos/{repo_url}/contents"
        try:
            requests.get(repo_api_url, headers=headers).raise_for_status()
        except requests.exceptions.RequestException as e:
            msg = f"Error accessing repository {repo_url}: {e}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "error", "data": {"description": msg, "done": True}}
                )
            return msg
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Fetching repository contents from {repo_name}...",
                        "done": False,
                    },
                }
            )
        contents = await self._fetch_directory_contents(
            repo_api_url, headers, __event_emitter__
        )
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "Repository contents fetched successfully.",
                        "done": True,
                        "hidden": False,
                    },
                }
            )
        messages_wrapper = {"messages": contents}
        self.filter.outlet(messages_wrapper)
        if contents:
            for item in contents:
                if item.get("type") == "file":
                    file_name = item.get("name", "Unknown")
                    file_url = item.get("url", "Unknown")
                    await emit_citation(
                        __event_emitter__,
                        [item.get("content", "")],
                        f"Repo: {repo_name}, File: {file_name}",
                        file_url,
                    )
        return messages_wrapper.get("messages")

    async def _find_repositories(
        self, partial_name: str, __event_emitter__=None
    ) -> List[str]:
        """
        Finds repositories in the owner that match the partial name.
        """
        owner = self.valves.owner
        access_token = self.valves.access_token
        if not owner or not access_token:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Missing owner or access token",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # Determine the API URL based on whether it's a user or org
        try:
            # Try to get org info - if it fails, assume it's a user
            user_api_url = f"https://api.github.com/orgs/{owner}"
            response = requests.get(user_api_url, headers=headers)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            api_url = f"https://api.github.com/orgs/{owner}/repos"  # It's an org
        except requests.exceptions.RequestException:
            # If the user API call fails, assume it's an organization
            api_url = f"https://api.github.com/users/{owner}/repos"  # It's a user

        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()
            repos = response.json()
            matching_repos = [
                repo["name"]
                for repo in repos
                if partial_name.lower() in repo["name"].lower()
            ]
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Found {len(matching_repos)} repos matching '{partial_name}'",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return matching_repos
        except requests.exceptions.RequestException as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error fetching repos: {e}",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []

    async def _fetch_issues_and_pulls(
        self, repo_name: str, state: str, __event_emitter__=None
    ) -> List[Dict[str, Any]]:
        """Fetches issues and pull requests from a repository."""
        owner = self.valves.owner
        access_token = self.valves.access_token
        max_items = (
            self.user_valves.max_items
        )  # max_items is per state (open and closed)
        if not owner or not access_token:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Missing owner or access token",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        repo_url = f"{owner}/{repo_name}"
        issues_api_url = f"https://api.github.com/repos/{repo_url}/issues?state={state}"
        pulls_api_url = f"https://api.github.com/repos/{repo_url}/pulls?state={state}"
        all_items = []
        try:
            # Fetch issues
            issues = await self._fetch_github_data(
                issues_api_url,
                headers,
                f"issues (state: {state})",
                max_items,
                __event_emitter__,
            )
            for issue in issues:
                issue_number = issue.get("number")
                if issue_number:
                    issue_comments = await self._fetch_issue_comments(
                        repo_name, issue_number, headers, __event_emitter__
                    )
                    issue["comments_content"] = issue_comments
                issue["type"] = "issue"  # Add a type identifier
                all_items.append(issue)
            # Fetch pull requests
            pulls = await self._fetch_github_data(
                pulls_api_url,
                headers,
                f"pull requests (state: {state})",
                max_items,
                __event_emitter__,
            )
            for pull in pulls:
                pull_number = pull.get("number")
                if pull_number:
                    pull_comments = await self._fetch_pull_request_comments(
                        repo_name, pull_number, headers, __event_emitter__
                    )
                    pull["comments_content"] = pull_comments
                pull["type"] = "pull"  # Add a type identifier
                all_items.append(pull)
        except requests.exceptions.RequestException as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error fetching issues/pulls: {e}",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []
        return all_items

    async def _fetch_issue_comments(
        self,
        repo_name: str,
        issue_number: int,
        headers: dict,
        __event_emitter__=None,
    ) -> List[Dict[str, Any]]:
        """Fetches comments for a specific issue."""
        owner = self.valves.owner
        max_comments = self.user_valves.max_comments
        if not owner or not self.valves.access_token:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Missing owner or access token",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []
        comments_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/issues/{issue_number}/comments"
        try:
            response = requests.get(comments_api_url, headers=headers)
            response.raise_for_status()
            comments = response.json()
            limited_comments = comments[:max_comments]
            # Debug: Print the fetched comments
            print(f"Fetched issue comments for issue #{issue_number}: {comments}")
            return limited_comments
        except Exception as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error fetching issue comments: {e}",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []

    async def _fetch_pull_request_comments(
        self,
        repo_name: str,
        pull_number: int,
        headers: dict,
        __event_emitter__=None,
    ) -> List[Dict[str, Any]]:
        """Fetches comments for a specific pull request."""
        owner = self.valves.owner
        max_comments = self.user_valves.max_comments
        if not owner or not self.valves.access_token:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Missing owner or access token",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []
        comments_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pull_number}/comments"
        try:
            response = requests.get(comments_api_url, headers=headers)
            response.raise_for_status()
            comments = response.json()
            limited_comments = comments[:max_comments]
            # Debug: Print the fetched comments
            print(f"Fetched pull request comments for PR #{pull_number}: {comments}")
            return limited_comments
        except Exception as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error fetching pull request comments: {e}",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []

    async def _fetch_pull_request_file_changes(
        self, repo_name: str, pull_number: int, __event_emitter__=None
    ) -> List[Dict[str, Any]]:
        """Fetches file changes for a specific pull request."""
        owner = self.valves.owner
        access_token = self.valves.access_token
        if not owner or not access_token:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Missing owner or access token",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        files_api_url = f"https://api.github.com/repos/{owner}/{repo_name}/pulls/{pull_number}/files"
        try:
            files = await self._fetch_github_data(
                files_api_url,
                headers,
                "pull request file changes",
                self.user_valves.max_items,
                __event_emitter__,
            )
            return files
        except Exception as e:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Error fetching pull request file changes: {e}",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return []

    async def analyze_repository(
        self,
        repo_name: str,
        include_files: bool = True,
        include_commits: bool = False,  # disabled as default because of rate limits and time
        user: dict = {},
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
    ):
        """Analyzes the content of a specified repository. It fetches all relevant data and lets the LLM handle specific queries.
        :param repo_name: The name of the repository to analyze OR a partial name to search for.
        :param include_files: Whether to include file contents in the analysis.
        :param include_commits: Whether to include recent commits in the analysis.
        """
        try:
            owner = self.valves.owner
            if not owner:
                return "owner not configured."
            headers = {
                "Authorization": f"token {self.valves.access_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            max_items = self.user_valves.max_items
            # First, check if the repo_name is a partial name
            matching_repos = await self._find_repositories(repo_name, __event_emitter__)
            if not matching_repos:
                return (
                    f"No repositories found matching '{repo_name}' in owner '{owner}'."
                )
            elif len(matching_repos) > 1:
                output = f"Multiple repositories found matching '{repo_name}':\n"
                for r in matching_repos:
                    output += f"- {r}\n"
                output += "Please specify the exact repository name to analyze."
                return output  # <---- Just return the list
            else:
                repo_name = matching_repos[
                    0
                ]  # Use the full name of the matched repository
                repo_url = f"{owner}/{repo_name}"
            output = f"Analysis of {repo_url}:\n"
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Starting repository analysis for {repo_name}...",
                            "done": False,
                        },
                    }
                )
            # Fetch repository files
            repository_data = {"files": [], "issues": [], "pulls": [], "commits": []}
            if include_files:
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": f"Fetching repository files...",
                                "done": False,
                            },
                        }
                    )
                file_contents = await self.fetch_repo_content(
                    repo_name, __event_emitter__
                )
                if isinstance(file_contents, str) and file_contents.startswith("Error"):
                    return file_contents  # Propagate the error message
                repository_data["files"] = file_contents
            # Fetch issues and pull requests (all states)
            for state in ["open", "closed"]:
                items = await self._fetch_issues_and_pulls(
                    repo_name, state, __event_emitter__
                )
                for item in items:
                    if item.get("type") == "issue":
                        repository_data["issues"].append(item)
                    elif item.get("type") == "pull":
                        repository_data["pulls"].append(item)
            # Fetch commits
            if include_commits:
                commits_api_url = f"https://api.github.com/repos/{repo_url}/commits"
                commits = await self._fetch_github_data(
                    commits_api_url, headers, "commits", max_items, __event_emitter__
                )
                repository_data["commits"] = commits
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "Analysis completed successfully.",
                            "done": True,
                            "hidden": False,
                        },
                    }
                )
            return repository_data
        except Exception as e:
            error_msg = f"An error occurred: {e}"
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "error", "data": {"description": error_msg, "done": True}}
                )
            return error_msg
