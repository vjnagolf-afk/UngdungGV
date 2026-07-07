# Thay thế phần hiển thị Bảng trong render_grade_manager_section bằng đoạn này:

        # Cấu hình bảng tối ưu cho phím mũi tên
        col_config = {
            "STT": st.column_config.NumberColumn("STT", width="small", disabled=True),
            "Họ và tên": st.column_config.TextColumn("Họ và tên", width="medium", disabled=True),
            "TX1": st.column_config.TextColumn("TX1", width="small"),
            "TX2": st.column_config.TextColumn("TX2", width="small"),
            "TX3": st.column_config.TextColumn("TX3", width="small"),
            "TX4": st.column_config.TextColumn("TX4", width="small"),
            "Điểm GK": st.column_config.TextColumn("Điểm GK", width="small"),
            "Điểm CK": st.column_config.TextColumn("Điểm CK", width="small"),
            "TBM HK": st.column_config.TextColumn("TBM HK", width="small", disabled=True),
            "Nhận xét": st.column_config.TextColumn("Nhận xét", width="medium")
        }

        # Dùng num_rows="fixed" để khóa bảng, tăng độ mượt cho phím mũi tên
        edited_df = st.data_editor(
            df_display,
            column_order=["STT", "Họ và tên", "TX1", "TX2", "TX3", "TX4", "Điểm GK", "Điểm CK", "TBM HK", "Nhận xét"],
            use_container_width=True,
            num_rows="fixed",
            column_config=col_config,
            hide_index=True,
            height=700,
            key="grade_editor"
        )
