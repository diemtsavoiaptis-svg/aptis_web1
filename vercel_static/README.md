# Bản Vercel/Firebase cho Điểm TSA Với Aptis

Thư mục này là bản web tĩnh để deploy lên Vercel. Bản này không lưu bài làm học sinh, chỉ đọc đề, đáp án, transcript và link audio.

## Chạy thử local

Từ thư mục `vercel_static`:

```powershell
..\venv\Scripts\python.exe -m http.server 5173
```

Mở:

```text
http://127.0.0.1:5173/
```

## Deploy Vercel

1. Đẩy repo lên GitHub.
2. Vào Vercel, import repo.
3. Chọn Root Directory là `vercel_static`.
4. Deploy.
5. Gắn domain `tsaptis.com` vào project trên Vercel.
6. Thêm cả `www.tsaptis.com` nếu muốn học sinh truy cập bằng www.

Domain chính:

```text
https://tsaptis.com
```

## Firebase

Nếu chưa cần admin sửa online, web vẫn chạy bằng file JSON tĩnh trong `data/listening-part-1.json`.

Khi muốn dùng Firestore:

1. Tạo Firebase project.
2. Bật Firestore Database.
3. Bật Authentication > Email/Password.
4. Tạo tài khoản admin.
5. Điền cấu hình Web App vào `firebase-config.js`.
6. Sửa email admin trong `firebase-config.js` và `firestore.rules`.
7. Publish Firestore Rules.
8. Mở `/seed.html`, đăng nhập admin và bấm đẩy Part 1.

Thiết kế dữ liệu Firestore:

```text
listeningParts/1/chunks/0001
listeningParts/1/chunks/0002
...
listeningMeta/part1
```

Mỗi chunk chứa tối đa 25 câu để giảm số lần đọc nhưng vẫn tránh document quá lớn.
