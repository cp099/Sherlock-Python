# Sherlock v2.0

**Sherlock is a comprehensive, self-hosted inventory and lending management system designed for school labs, makerspaces, and workshops.**

This project is a complete, ground-up rewrite and significant feature expansion of the original [Sherlock v1.0](https://github.com/Atal-Lab-DPSBS/Sherlock). It migrates the application from Ruby on Rails to a modern, robust, and scalable Python and Django backend, transforming it from a simple inventory list into a powerful lab management platform.

## 🌟 Mission

The goal of Sherlock v2.0 is to provide a powerful, easy-to-deploy, and intuitive tool for lab managers to track their physical inventory. It answers the critical questions of lab management:
*   **What** do we have and **where** is it?
*   **Who** has borrowed our equipment?
*   **When** is it due back?
*   **What** is our inventory's lifecycle?

## ✨ Core Features

Sherlock is built on two major pillars: **Inventory Management** and a **Lending System**.

### Inventory Management
*   **Hierarchical Structure:** Organize your inventory logically with **Sections** (e.g., "Electronics Workbench"), **Spaces** (e.g., "Drawer M1"), and **Items** (e.g., "MQ-2 Gas Sensor").
*   **Stock Control:** Track the quantity of each item, with a full audit trail for every stock change (e.g., "Received New Stock," "Reported Damaged").
*   **Label Printing:** Generate and print custom barcode and QR code labels for your items, spaces, and sections to seamlessly bridge your physical and digital inventory.
*   **Powerful Search:** A unified search dashboard to find any item, space, or student record in the system.

### Advanced Lending System
*   **Student Records:** Maintain a simple, secure database of students who can borrow items.
*   **Kiosk-Style Checkout Terminal:** A dedicated, fast interface for lab managers to check out items to students. Features a live, as-you-type search for both students (by name or ID) and items (by name or barcode).
*   **Stock Validation:** The system automatically checks available stock before allowing a checkout, preventing over-lending.
*   **Partial Returns:** A sophisticated check-in system that allows for partial returns and keeps a complete, auditable log of every transaction.
*   **Due Date & Overdue Tracking:** Assign a due date to every loan. The system includes a central "On Loan" dashboard and a dedicated "Overdue Items" report.

### Modern Technology
*   **Camera Scanning:** Use your device's camera to scan item barcodes for rapid checkouts or to use the "Universal Lookup" tool to instantly identify any item, space, or section from anywhere in the app.
*   **Data Visualizations:** The main dashboard features charts for weekly loan activity and most popular items, providing instant insight into your lab's operations.

## 🚀 Deployment

Sherlock is designed for incredibly simple deployment in an institutional environment, without requiring any knowledge of Python or Django on the part of the end-user.

The application is packaged as a **standalone executable** using PyInstaller. This bundle contains the entire application, a production-grade web server, and all its dependencies.

### How to Run Sherlock:
1.  Go to the [**Releases**](https://github.com/your-username/Sherlock-python/releases) page of this repository.
2.  Download the latest `.zip` file for your operating system (e.g., `Sherlock-v2.0.0-Windows.zip`).
3.  Unzip the file. This will create a single `Sherlock` folder.
4.  Inside the folder, double-click the `Sherlock` executable (`Sherlock.exe` on Windows).

A terminal window will open, and the server will start. The first time it runs, it will automatically create a new, empty `db.sqlite3` database file inside its folder. You can then access the application in your web browser at `http://127.0.0.1:8000`.

To make it accessible to other computers on the same network, find the local IP address of the machine running Sherlock (e.g., `192.168.1.10`) and access it at `http://192.168.1.10:8000`.

## 💻 For Developers: Running from Source

If you want to run the application in a development environment:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Sherlock-python.git
    cd Sherlock-python
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    .\venv\Scripts\activate   # On Windows
    ```
3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the initial database migrations:**
    ```bash
    python manage.py migrate
    ```
5.  **Create a superuser account:**
    ```bash
    python manage.py createsuperuser
    ```
6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```

## 🛠️ Built With
*   **Backend:** Python 3, Django 5.1
*   **Frontend:** HTML, CSS, HTMX, Chart.js
*   **Server:** Waitress
*   **Packaging:** PyInstaller

---
This project is a testament to the power of iterative development and a great example of modernizing an existing application with new technologies and features.