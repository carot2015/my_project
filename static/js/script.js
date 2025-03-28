window.addEventListener('pageshow', function(event) {
  if (event.persisted) {
    window.location.reload();
  }
});
document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('loginForm');
  const errorMessage = document.getElementById('error-message');
  const loginButton = document.getElementById('loginButton');
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');

  // **Reset trạng thái khi trang được tải**
  if (loginButton) {
    loginButton.disabled = false; // Mở khóa nút "Đăng nhập"
    loginButton.innerHTML = 'Đăng nhập'; // Đặt lại nội dung ban đầu
  }

  if (errorMessage) {
    errorMessage.style.display = 'none'; // Ẩn thông báo lỗi
    errorMessage.textContent = ''; // Xóa nội dung lỗi
  }

  if (usernameInput && passwordInput) {
    usernameInput.classList.remove('shake'); // Xóa hiệu ứng "shake"
    passwordInput.classList.remove('shake'); // Xóa hiệu ứng "shake"
  }

  // **Lắng nghe sự kiện submit của form**
  if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
      event.preventDefault(); // Ngăn hành động mặc định khi submit form

      // Lấy giá trị nhập từ các input
      const username = usernameInput.value.trim();
      const password = passwordInput.value;

      // Xóa thông báo lỗi và hiệu ứng cũ
      errorMessage.style.display = 'none';
      errorMessage.textContent = '';
      usernameInput.classList.remove('shake');
      passwordInput.classList.remove('shake');

      // **Kiểm tra nếu input trống**
      if (username === '' && password === '') {
        errorMessage.textContent = 'Bạn chưa đăng nhập';
        errorMessage.style.display = 'block';
        usernameInput.classList.add('shake');
        passwordInput.classList.add('shake');
        return;
      } else if (!username || !password) {
        errorMessage.textContent = 'Vui lòng điền đầy đủ thông tin.';
        errorMessage.style.display = 'block';
        usernameInput.classList.add('shake');
        passwordInput.classList.add('shake');
        return;
      }

      // **Hiển thị trạng thái đang xử lý**
      loginButton.disabled = true; // Vô hiệu hóa nút trong khi xử lý
      loginButton.innerHTML = 'Đang đăng nhập<span class="spinner"></span>';

      // Tạo URLSearchParams để đóng gói dữ liệu
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      // **Gửi dữ liệu tới backend qua Fetch API**
      fetch('/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      })
        .then(response => response.json())
        .then(data => {
          console.log('Response from server:', data); // Debug kết quả từ server
          // Nếu server trả về "success", chuyển hướng dựa trên vai trò
          if (data.status === 'success') {
            if (data.role === 'admin') {
              // Nếu admin, chuyển hướng đến trang quản trị
              window.location.href = '/admin';
            } else {
              // Nếu không phải admin, chuyển hướng đến trang chọn môn thi
              window.location.href = '/choose_exam';
            }
          } else {
            // Nếu không, hiển thị thông báo lỗi từ backend
            errorMessage.style.display = 'block';
            errorMessage.textContent = data.message;
            // Reset lại button đăng nhập
            loginButton.disabled = false;
            loginButton.innerHTML = 'Đăng nhập';
          }
        })
        .catch(error => {
          console.error('Error:', error);
          // Nếu xảy ra lỗi (ví dụ mất kết nối)
          errorMessage.style.display = 'block';
          errorMessage.textContent = 'Có lỗi xảy ra. Vui lòng thử lại sau.';
          // Reset lại button đăng nhập
          loginButton.disabled = false;
          loginButton.innerHTML = 'Đăng nhập';
        });
    });
  }
});
