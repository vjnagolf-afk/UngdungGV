def load_class_menu(self):
        selected_grade = self.menu_grade.get()
        
        # Cấu hình danh sách lớp theo yêu cầu của thầy
        class_config = {
            "6": ["6A", "6B", "6C", "6D", "6E", "6F"],
            "7": ["7A", "7B", "7C", "7D", "7E", "7F"],
            "8": ["8A", "8B", "8C", "8D", "8E", "8F"],
            "9": ["9A", "9B", "9C", "9D", "9E", "9F", "9G"]
        }
        
        available_classes = []
        
        if selected_grade == "Tất cả khối" or not selected_grade:
            for classes in class_config.values():
                available_classes.extend(classes)
        else:
            # Trích xuất số khối an toàn
            grade_num = "".join([c for c in selected_grade if c.isdigit()])
            if grade_num in class_config:
                available_classes = class_config[grade_num]
        
        # Thêm các lớp đặc biệt từ Database nếu có (đề phòng trường hợp ngoài danh sách chuẩn)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT classroom FROM students WHERE classroom IS NOT NULL")
            db_classes = [row[0] for row in cursor.fetchall()]
            for dc in db_classes:
                if dc not in available_classes:
                    available_classes.append(dc)
            conn.close()
        except:
            pass
            
        self.menu_class["options"] = sorted(list(set(available_classes))) # Sử dụng options cho Streamlit
        # Cập nhật lại widget selectbox lớp trong Streamlit
        st.session_state["class_options"] = sorted(list(set(available_classes)))
        self.load_data_to_grid()
