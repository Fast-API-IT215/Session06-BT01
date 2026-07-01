from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(title="API Quản lý khóa học")

# 1. Dữ liệu mẫu ban đầu
courses = [
    {"id": 1, "code": "PY101", "name": "Python Basic", "duration": 30, "fee": 3000000.0},
    {"id": 2, "code": "API101", "name": "FastAPI Basic", "duration": 24, "fee": 2500000.0},
    {"id": 3, "code": "JV101", "name": "Java Basic", "duration": 40, "fee": 4000000.0}
]

# 2. Pydantic Schemas để validate dữ liệu đầu vào
class CourseCreate(BaseModel):
    code: str = Field(..., description="Mã khóa học không được trùng")
    name: str = Field(..., min_length=1, description="Tên khóa học không được rỗng")
    duration: int = Field(..., gt=0, description="Thời lượng phải lớn hơn 0")
    fee: float = Field(..., ge=0, description="Học phí phải lớn hơn hoặc bằng 0")

class CourseUpdate(BaseModel):
    code: str = Field(..., description="Mã khóa học")
    name: str = Field(..., min_length=1, description="Tên khóa học không được rỗng")
    duration: int = Field(..., gt=0, description="Thời lượng phải lớn hơn 0")
    fee: float = Field(..., ge=0, description="Học phí phải lớn hơn hoặc bằng 0")

class CourseResponse(BaseModel):
    id: int
    code: str
    name: str
    duration: int
    fee: float


# ==================== ENDPOINTS ====================

# [GET] Lấy danh sách khóa học kèm Tìm kiếm và Lọc (Query Params)
@app.get("/courses", response_model=List[CourseResponse])
def get_courses(
    keyword: Optional[str] = Query(None, description="Tìm theo name hoặc code"),
    min_fee: Optional[float] = Query(None, description="Học phí từ mức này trở lên"),
    max_fee: Optional[float] = Query(None, description="Học phí nhỏ hơn hoặc bằng mức này")
):
    filtered_courses = courses
    
    # Lọc theo từ khóa (keyword)
    if keyword:
        keyword_lower = keyword.lower()
        filtered_courses = [
            c for c in filtered_courses 
            if keyword_lower in c["name"].lower() or keyword_lower in c["code"].lower()
        ]
        
    # Lọc theo học phí tối thiểu (min_fee)
    if min_fee is not None:
        filtered_courses = [c for c in filtered_courses if c["fee"] >= min_fee]
        
    # Lọc theo học phí tối đa (max_fee)
    if max_fee is not None:
        filtered_courses = [c for c in filtered_courses if c["fee"] <= max_fee]
        
    return filtered_courses


# [GET] Lấy chi tiết một khóa học theo ID
@app.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_detail(course_id: int):
    for course in courses:
        if course["id"] == course_id:
            return course
    raise HTTPException(status_code=404, detail="Course not found")


# [POST] Thêm khóa học mới
@app.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(course_data: CourseCreate):
    # Kiểm tra điều kiện: code không được trùng
    for course in courses:
        if course["code"].upper() == course_data.code.upper():
            raise HTTPException(status_code=400, detail="Course code already exists")
            
    # Tự động tăng ID
    new_id = max([c["id"] for c in courses]) + 1 if courses else 1
    
    new_course = {
        "id": new_id,
        "code": course_data.code,
        "name": course_data.name,
        "duration": course_data.duration,
        "fee": course_data.fee
    }
    courses.append(new_course)
    return new_course


# [PUT] Cập nhật khóa học
@app.put("/courses/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, course_data: CourseUpdate):
    target_course = None
    for course in courses:
        if course["id"] == course_id:
            target_course = course
            break
            
    # Nếu không tìm thấy ID
    if not target_course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    # Kiểm tra trùng mã code với các khóa học KHÁC khóa học đang sửa
    for course in courses:
        if course["id"] != course_id and course["code"].upper() == course_data.code.upper():
            raise HTTPException(status_code=400, detail="Course code already exists")
            
    # Cập nhật thông tin
    target_course["code"] = course_data.code
    target_course["name"] = course_data.name
    target_course["duration"] = course_data.duration
    target_course["fee"] = course_data.fee
    
    return target_course


# [DELETE] Xóa khóa học
@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int):
    global courses
    for i, course in enumerate(courses):
        if course["id"] == course_id:
            courses.pop(i)
            return  # Trả về 204 No Content thành công
            
    # Nếu không tìm thấy để xóa
    raise HTTPException(status_code=404, detail="Course not found")