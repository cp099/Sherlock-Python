# Sherlock v2.0 - Website & Feature Map

This document outlines the complete structure and user flow of the Sherlock application. It serves as a high-level guide for understanding the relationship between different pages and features.

---

### 1.0 Public-Facing Pages (User Not Logged In)

-   **`/` - Landing Page (`homepage`)**
    -   Displays the Sherlock logo.
    -   Provides two main actions:
        -   `->` **Login Button** (links to `/accounts/login/`)
        -   `->` **Sign Up Button** (links to `/accounts/signup/`)

-   **`/accounts/login/` - Login Page**
    -   Form for existing users to log in.
    -   Link to the Sign Up page.
    -   Link to the Password Reset flow.

-   **`/accounts/signup/` - Sign Up Page**
    -   Form for new users to create an account.
    -   Link to the Login page.

-   **`/accounts/password_reset/` - Password Reset Flow**
    -   A series of standard pages for users to reset a forgotten password.

---

### 2.0 Main Application (User Logged In)

Upon logging in, the user is directed to the main application, which is structured around the sidebar navigation.

-   **`/dashboard/` - The Dashboard (`homepage` for logged-in users)**
    -   **Metric Cards:**
        -   Items on Loan
        -   Items Overdue
        -   Low Stock Items
        -   New Students This Month
    -   **Activity Feeds:**
        -   Recently Checked Out (Today)
        -   Items Due Soon (Next 3 Days)
    -   **Data Visualizations:**
        -   Loan Activity (Last 7 Days) Bar Chart
        -   Most Popular Items Pie Chart

#### 2.1 Inventory

-   **`/browse/` - Inventory Browser**
    -   **Column 1: Sections**
        -   Displays a list of all Sections.
        -   Includes a **"+ Add"** link to the *Section Create Page*.
        -   *Clicking a Section populates Column 2 and the Preview Pane.*
    -   **Column 2: Spaces**
        -   Displays a list of Spaces within the selected Section.
        -   *Clicking a Space populates Column 3 and the Preview Pane.*
    -   **Column 3: Items**
        -   Displays a list of Items within the selected Space.
        -   *Clicking an Item populates the Preview Pane.*
    -   **Preview Pane:**
        -   Shows a summary of the selected Section, Space, or Item.
        -   Provides a link to the **View Full Details** page.
        -   Contextually provides **"Add New Space"** or **"Add New Item"** buttons.

-   **`/sections/<id>/` - Section Detail Page**
    -   Shows full details, QR code, and action buttons.
    -   `->` **Edit Details Page**
    -   `->` **Add to Print Queue** action
    -   `->` **Delete Section** action

-   **`/sections/<id>/spaces/<id>/` - Space Detail Page**
    -   Shows full details, QR code, and action buttons.
    -   `->` **Edit Details Page** (includes **Relocate Space** functionality)
    -   `->` **Add to Print Queue** action
    -   `->` **Delete Space** action

-   **`/sections/<id>/spaces/<id>/items/<id>/` - Item Detail Page**
    -   Shows full details, barcode, and two-column layout.
    -   **Left Column (Status & Actions):**
        -   `->` **Edit Details Page** (includes **Relocate Item** functionality)
        -   `->` **Receive Stock Page**
        -   `->` **Report Damaged Page**
        -   `->` **Add Small/Large Label to Print Queue** actions
        -   `->` **Delete Item** action
    -   **Right Column (Audit Trails):**
        -   **Loan History Audit Trail** (filterable and scrollable)
        -   **Inventory History Log** (filterable and scrollable)

-   **`/low-stock-report/` - Low Stock Report Page**
    -   Displays a list of all items with a quantity of 5 or less.

#### 2.2 Management

-   **`/students/` - Student Records Page**
    -   Displays a list of all students.
    -   Includes a filter for student class.
    -   `->` **Add a New Student** button

-   **`/students/<id>/` - Student Detail Page**
    -   Shows full student details.
    -   Displays **Items Currently on Loan** table.
    -   Displays **Full Loan History** table.
    -   `->` **Edit Student Record** link
    -   `->` **Delete Student** action

-   **`/on-loan/` - On Loan Dashboard**
    -   Shows a list of all items currently checked out across all students.
    -   `->` **Go to Checkout Terminal** button
    -   `->` **Check In Page** for each item

-   **`/check-in/<id>/` - Check In Page**
    -   Form to process a full or **partial return** of a loaned item.

-   **`/overdue-report/` - Overdue Items Report Page**
    -   Displays a filtered list of only items that are past their due date.

#### 2.3 Tools

-   **Universal Scan** (Modal)
    -   Accessible from the sidebar and Search Page.
    -   Opens a camera view to scan any barcode or QR code.
    -   *Redirects to the corresponding Item, Space, or Section page.*

-   **`/search/` - Unified Search Page**
    -   **Item Search:** Live, as-you-type search for all inventory items.
    -   **Student Search:** Live, as-you-type search for all students.

-   **`/print/` - Print Queue Page**
    -   Displays all labels added to the user's personal queue.
    -   Allows for changing quantity and deleting items.
    -   `->` **Go to Print Shop** link

-   **`/print-shop/` -> `/print-page/` - Print Page Flow**
    -   An instructions page that leads to the final, multi-label print layout optimized for paper.

#### 2.4 Account

-   **(Future) `/profile/` - User Profile Page**
    -   Allows a user to change their name, email, and password.
-   **Logout**
    -   Logs the user out and redirects to the public Landing Page.