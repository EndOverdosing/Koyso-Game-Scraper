![Vyla Games Logo](/images/github-banner.jpg)

# Vyla Games

Vyla Games is a performant and user-centric web platform for accessing unblocked web-based games. The project is built with a focus on a clean user interface, fast load times, and ease of content management.

## Features

-   **Responsive User Interface:** The design is fully responsive, ensuring a seamless experience across desktops, tablets, and mobile devices.
-   **Dynamic Content Loading:** The game library is populated dynamically from a `games.json` manifest file, allowing for easy updates and management without altering the core application code.
-   **Real-Time Search:** Includes a client-side search functionality that filters the game library instantly as the user types.
-   **Modal Game Player:** Games are launched within a modal overlay, providing an integrated user experience that avoids page reloads or redirects.
-   **Light and Dark Themes:** A user-configurable theme toggle allows for switching between light and dark modes to suit user preference.
-   **Animated Background:** Features an animated background created from a dynamic collage of game art, enhancing visual engagement.
-   **Progressive Web App (PWA) Support:** Includes a `manifest.json` file, enabling users to install the website on their home screen for an app-like experience.
-   **Static Site Architecture:** Built with standard HTML, CSS, and JavaScript, the project requires no complex build process and is simple to customize and deploy.

## Technology Stack

-   HTML5
-   CSS3 (with Custom Properties)
-   Vanilla JavaScript (ES6+)
-   Font Awesome (Icons)

## Local Development Setup

Follow these instructions to set up a local instance of the project for development or testing.

### Prerequisites

-   A code editor (e.g., Visual Studio Code)
-   A local web server to serve the static files. This is necessary for the `fetch` API to work correctly with local files.

### Installation

1.  Clone the repository to your local machine:
    ```sh
    git clone https://github.com/your-username/vyla-games.git
    ```

2.  Navigate to the project directory:
    ```sh
    cd vyla-games
    ```

3.  Serve the project files using a local server. A recommended method is using the **Live Server** extension for Visual Studio Code.
    -   Install the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension from the VS Code Marketplace.
    -   Right-click on `index.html` and select "Open with Live Server".

    Alternatively, you can use Python's built-in HTTP server:
    ```sh
    # If you have Python 3 installed
    python -m http.server
    ```
    After starting the server, open your web browser and navigate to `http://localhost:8000`.

## Project Structure

The repository is organized with a clear and straightforward structure:

```
vyla-games/
├── g/                      # Contains individual game builds (HTML, JS, assets)
├── images/                 # Contains game posters, favicons, and site assets
├── js/
│   └── index.js            # Core application logic for the homepage
├── styling/
│   └── index.css           # All application styles
├── about-us.html           # The "About Us" static page
├── games.json              # The JSON manifest for the game library
├── index.html              # The main entry point of the application
├── manifest.json           # PWA configuration file
├── privacy-policy.html     # The "Privacy Policy" static page
└── terms-of-service.html   # The "Terms of Service" static page
```

## Content Management

To add a new game to the platform, follow these steps:

1.  **Add Game Files:** Place the game's build files (including its `index.html` and any related assets) into a new sub-folder within the `/g/` directory.

2.  **Add Poster Image:** Add a corresponding poster image for the game to the `/images/` directory.

3.  **Update the Game Manifest:** Open `games.json` and add a new JSON object to the main array. The object must conform to the following structure:
    ```json
    {
        "title": "Game Title",
        "description": "A brief and informative description of the game.",
        "image": "images/game-poster.png",
        "url": "g/game-folder/index.html"
    }
    ```
    -   `title`: The display name of the game.
    -   `description`: A short summary of the game.
    -   `image`: The relative path to the poster image.
    -   `url`: The relative path to the game's main HTML file.

After saving `games.json`, the new game will automatically be available in the library.

## Deployment

This project consists of static assets, making it suitable for deployment on any static hosting provider. Services like Vercel, Netlify, or GitHub Pages are highly recommended for their ease of use.

**Recommended Deployment via Vercel/Netlify:**

1.  Create a free account on [Vercel](https://vercel.com/) or [Netlify](https://www.netlify.com/).
2.  Connect your GitHub account and import this repository.
3.  The platform will automatically detect the static nature of the project. No build commands or output directories are required.
4.  Click "Deploy". The site will be live within moments.

## Contributing

Contributions to this project are welcome. If you wish to contribute, please fork the repository and create a pull request with your proposed changes.

1.  Fork the repository.
2.  Create a new branch for your feature (`git checkout -b feature/NewFeature`).
3.  Commit your changes (`git commit -m 'Add NewFeature'`).
4.  Push to your branch (`git push origin feature/NewFeature`).
5.  Open a pull request for review.

## License

This project is distributed under the MIT License. See the `LICENSE` file for more information.