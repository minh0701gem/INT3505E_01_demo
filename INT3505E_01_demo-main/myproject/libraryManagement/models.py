from mongoengine import connect, Document, StringField, IntField, ReferenceField

# Kết nối tới database MongoDB
connect('library_db', host='mongodb://localhost/library_db')

class Author(Document):
    name = StringField(required=True, max_length=100)
    bio = StringField()

class Book(Document):
    title = StringField(required=True, max_length=200)
    published_year = IntField()
    quantity = IntField(default=1)
    # Tạo quan hệ: một cuốn sách thuộc về một tác giả
    author = ReferenceField(Author)