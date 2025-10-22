# Library Management System API

Đây là một dự án API đơn giản được xây dựng bằng Flask để quản lý các đầu sách trong một thư viện. Dự án này bao gồm các chức năng cơ bản để quản lý sách, tác giả, thành viên và các lượt mượn sách.

API được tài liệu hóa bằng chuẩn **OpenAPI 3.0 (Swagger)**, cung cấp một giao diện tương tác để dễ dàng khám phá và thử nghiệm các endpoint.

## Tính năng

-   Quản lý Sách (Thêm/Xem)
-   Quản lý Tác giả (Thêm/Xem)
-   API Specification được xây dựng bằng OpenAPI.
-   Giao diện Swagger UI tương tác để thử nghiệm API.

## Cấu trúc dự án

```
libraryManagement/
├── __pycache__/
├── app.py          # Lớp API (Flask routes, OpenAPI specs)
├── db.py           # Lớp logic truy cập cơ sở dữ liệu
├── library.db      # File cơ sở dữ liệu SQLite
├── schema.sql      # Schema để khởi tạo cơ sở dữ liệu
└── README.md       # Tài liệu dự án
```

## Data Modeling (Mô hình hóa Dữ liệu)

Hệ thống được xây dựng dựa trên 4 thực thể chính:

1.  **Author (Tác giả)**
    -   `id`: INTEGER (Khóa chính)
    -   `name`: TEXT
    -   `bio`: TEXT

2.  **Book (Sách)**
    -   `id`: INTEGER (Khóa chính)
    -   `title`: TEXT
    -   `isbn`: TEXT (UNIQUE)
    -   `published_year`: INTEGER
    -   `quantity`: INTEGER
    -   `author_id`: INTEGER (Khóa ngoại đến `authors.id`)

3.  **Member (Thành viên)**
    -   `id`: INTEGER (Khóa chính)
    -   `name`: TEXT
    -   `email`: TEXT (UNIQUE)
    -   `join_date`: TIMESTAMP

4.  **Loan (Lượt mượn)**
    -   `id`: INTEGER (Khóa chính)
    -   `book_id`: INTEGER (Khóa ngoại đến `books.id`)
    -   `member_id`: INTEGER (Khóa ngoại đến `members.id`)
    -   `loan_date`: TIMESTAMP
    -   `return_date`: TIMESTAMP (NULL nếu chưa trả)
    -   `status`: TEXT ('borrowed' hoặc 'returned')

## Resource Design (Thiết kế Tài nguyên API)

API được thiết kế theo các nguyên tắc RESTful. Các tài nguyên chính bao gồm:

-   `/authors`: Quản lý tác giả.
-   `/books`: Quản lý sách.
-   `/members`: Quản lý thành viên.
-   `/loans`: Quản lý các lượt mượn/trả sách.

### Chi tiết các Endpoint

| Method | Endpoint                    | Mô tả                                      |
|--------|-----------------------------|--------------------------------------------|
| `GET`  | `/authors`                  | Lấy danh sách tất cả tác giả.              |
| `POST` | `/authors`                  | Tạo một tác giả mới.                       |
| `GET`  | `/authors/{id}`             | Lấy thông tin một tác giả cụ thể.          |
| `GET`  | `/authors/{id}/books`       | Lấy danh sách sách của một tác giả.        |
| `GET`  | `/books`                    | Lấy danh sách tất cả sách.                 |
| `POST` | `/books`                    | Thêm một cuốn sách mới.                    |
| `GET`  | `/books/{id}`               | Lấy thông tin một cuốn sách cụ thể.        |
| `POST` | `/loans`                    | Tạo một lượt mượn sách mới.                |
| `PUT`  | `/loans/{id}/return`        | Đánh dấu một lượt mượn là đã trả.          |

*(Các endpoint `PUT`, `DELETE` cho các tài nguyên sẽ được phát triển trong tương lai.)*

## Hướng dẫn cài đặt và sử dụng

### Yêu cầu

-   Python 3.x
-   pip

### Cài đặt

1.  Clone repository về máy:
    ```bash
    git clone https://github.com/minh0701gem/INT3505E_01_demo.git
    cd INT3505E_01_demo/INT3505E_01_demo-main/myproject/libraryManagement
    ```

2.  Cài đặt các thư viện cần thiết:
    ```bash
    pip install Flask flasgger
    ```

3.  Khởi tạo cơ sở dữ liệu từ file schema:
    *(Nếu file `library.db` đã tồn tại, hãy xóa nó trước để tạo lại từ đầu)*
    ```bash
    sqlite3 library.db < schema.sql
    ```

4.  Chạy ứng dụng Flask:
    ```bash
    flask run
    ```
    Hoặc:
    ```bash
    python app.py
    ```
    Server sẽ chạy tại `http://127.0.0.1:5000`.

## API Specification và Thử nghiệm

Dự án sử dụng **Flasgger** để tự động tạo tài liệu API từ mã nguồn theo chuẩn OpenAPI 3.0.

1.  Sau khi khởi động server, mở trình duyệt và truy cập:
    ```
    http://127.0.0.1:5000/apidocs/
    ```
2.  Bạn sẽ thấy giao diện Swagger UI, nơi bạn có thể:
    -   Xem tất cả các endpoint có sẵn.
    -   Xem chi tiết về các tham số, request body, và các response có thể có.
    -   Sử dụng nút **"Try it out"** để gửi yêu cầu và thử nghiệm API trực tiếp từ trình duyệt.

Chúc bạn có trải nghiệm tốt với API này!