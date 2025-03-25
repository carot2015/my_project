document.addEventListener("DOMContentLoaded", function() {
    // Lấy form đăng ký qua id
    const registerForm = document.getElementById("registerForm");
    // Lấy phần tử hiển thị thông báo lỗi
    const errorElement = document.getElementById("client-error");
  
    if (registerForm) {
      registerForm.addEventListener("submit", function(event) {
        // Lấy giá trị từ các trường input
        const fullname = document.getElementById("fullname").value.trim();
        const email = document.getElementById("email").value.trim();
        const username = document.getElementById("username").value.trim();
        const password = document.getElementById("password").value;
        const confirmPassword = document.getElementById("confirm_password").value;
  
        // Ẩn thông báo lỗi trước mỗi lần kiểm tra
        if (errorElement) {
          errorElement.style.display = "none";
        }
  
        // Kiểm tra nếu người dùng để trống bất kỳ trường nào
        if (!fullname || !email || !username || !password || !confirmPassword) {
          event.preventDefault(); // Ngăn việc submit form
          if (errorElement) {
            errorElement.textContent = "Vui lòng điền đầy đủ thông tin!";
            errorElement.style.display = "block";
            errorElement.style.color = "red"; // Hiển thị thông báo lỗi màu đỏ
          }
          return; // Dừng xử lý
        }
  
        // Kiểm tra nếu mật khẩu và xác nhận mật khẩu không khớp
        if (password !== confirmPassword) {
          event.preventDefault(); // Ngăn việc submit form
          if (errorElement) {
            errorElement.textContent = "Mật khẩu không khớp!";
            errorElement.style.display = "block";
            errorElement.style.color = "red"; // Hiển thị thông báo lỗi màu đỏ
          }
          return; // Dừng xử lý
        }
  
        // Nếu form hợp lệ
        console.log("Form hợp lệ, chuẩn bị submit");
        // Có thể thêm hiệu ứng spinner hoặc disable nút submit nếu cần
      });
    }
  });
  