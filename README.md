# GitAccess

![GitAccess Logo](https://i.imgur.com/1PxbyHA.png)

**GitAccess** is a tool that enables LLM models to connect to GitHub repositories within a specified account or organization to fetch their contents, issues, pull requests, and more. This allows you to query the model about the current state of a project and stay up-to-date.

## 📦 Description

*   **Authors:** ErrorRExorY/CptExorY, [SeveighTech](https://seveightech.com)), [Josetseph](https://github.com/josetseph))
*   **Author Website:** [pascal-frerks.de](https://pascal-frerks.de)
*   **GitHub Repository:** [GitAccess on GitHub](https://github.com/WhyWaitServices/open-webui-gitaccess.git)
*   **Required OpenWebUI Version:** 0.6.0
*   **Version:** 0.2.0 (Updated by SeveighTech)
*   **License:** MIT

**Key Updates by SeveighTech (Version 0.2.0):**

*   Added support for fetching issues, pull requests, comments, and file changes in pull requests.
*   Implemented repository search by partial name.
*   Introduced configurable limits for the number of items and comments fetched.
*   Improved error handling and status updates.

## 🚀 Installation

To install GitAccess in your self-hosted OpenWebUI instance, you can follow these steps:

### Via the Marketplace

1.  Open your OpenWebUI instance.
2.  Go to the [Marketplace](https://openwebui.com/t/cptexory/gitaccess "Marketplace").
3.  Add the link to GitAccess: `https://github.com/WhyWaitServices/open-webui-gitaccess.git`.

### Manual Installation

1.  Copy the code from the `GitAccess.py` file.
2.  Add the copied code to your OpenWebUI instance by creating a new tool under Workspace > Tools.
3.  Paste the copied code from the `GitAccess.py` file into the large input field and assign a name and a description.
4.  Save the tool.

## ⚙️ Configuration

### Environment Variables (Valves)

*   **Accessing the Valves:** The environment variables for the tool are set within OpenWebUI. Click the gear button when you open the tool to configure the valves.

    *   **access_token:** A personal access token from GitHub that has the necessary permissions to access the repository.
    *   **owner:** The name of the GitHub account/organization (e.g., `SeveighTech`).

### UserValves

*   **Setting UserValves:** If you have activated the tool in a chat or model, you can set the UserValves using the "Controls" button (located at the top right, directly left of the profile picture). A sheet will open where you can configure the UserValves of the tool.

    *   **max_files:** Maximum number of files per directory to fetch.
    *   **truncate_content:** Whether to truncate large files for better readability.
    *   **max_content_length:** Maximum character length for file contents when truncation is enabled.
    *   **max_items:** Maximum number of issues, pull requests, etc., to retrieve per state (open/closed).
    *   **max_comments:** Maximum number of comments to retrieve for issues and pull requests.

## 🛠️ Usage

After installation, you can use GitAccess as follows:

1.  Ensure that you are correctly configured (access token and owner).
2.  Launch the tool in your OpenWebUI instance.
3.  Use simple prompts like:

    *   "What are the pull requests, pull request comments, and the pull request file changes on the `{repository_name}` repository?"
    *   "Tell me more about the `{repository_name}` repository."
    *   "Give me all the comments on each issue on the `{repository_name}` repository."
    *   "Are there any issues or pull requests in the repository: `{repository_name}`"
    *   "Get all the information about all the pull requests on the `{repository_name}` repository. Using *only* that information, tell me which comments are on pull request number `{PR_number}`. Do *not* use the tool again."

The response might look like this:
![Example Screenshot](https://i.imgur.com/tPMQwyf.png)

The status of actions will be displayed in the user interface through status messages.

## 🤖 Features

*   **Fetching Repository Contents:** Read the structure and files of a specified GitHub repository.
*   **Dynamic Filters:** Distinguish between directories and files to efficiently retrieve the desired data.
*   **Event Emitter:** Real-time feedback on the progression of queries and other actions.
*   **Issue and Pull Request Analysis:** Fetch and analyze issues, pull requests, and associated comments.
*   **Repository Search:** Find repositories by partial name within the configured owner.

## 📋 License

This project is licensed under the MIT License. For more information, please refer to the [LICENSE](LICENSE) file.

## 🤝 Contributing

Contributions are welcome! Please open an issue or a pull request to share suggestions or propose improvements.

## 📞 Contact

For questions or feedback, feel free to leave an issue.

Thank you for using GitAccess!