$(document).on('click', '.show-thumnail', function () {
    var id = $(this).data('id'); // Bổ sung biến id
    console.log(id);
    var page = 1;
    $('#use-id-count-image').val(id);
    show_image(id, page);
});

$(document).on('click', '#page-image .page-link-one', function (e) {
    e.preventDefault();
    var url = $(this).attr('href');
    page = url.split('page=')[1];
    id = $('#use-id-count-image').val();
    show_image(id, page);
});



function show_image(id, page) {
    var formData = new FormData(); // Khởi tạo FormData bên trong hàm
    formData.append('id', id);
    formData.append('page', page);
    formData.append('current_date_old', $('#input-date-upload-old').val());
    formData.append('current_date_new', $('#input-date-upload-new').val());
    formData.append('action', 'show-thumnail');
    let host = window.location.host;
    let protocol = window.location.protocol;

    $.ajax({
        url: `${protocol}//${host}/count-data/`,
        type: 'POST',
        headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success === true) {
                $('#image-img').empty();
                $('#image-img').html(response.thumnail_html);
                $('#page-image').empty();
                $('#page-image').html(response.page_bar_html);
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}



$(document).on('click', '.show-title', function () {
    var id = $(this).data('id'); // Bổ sung biến id
    var page = 1;
    $('#use-id-count-title').val(id);
    show_title(id, page);
});

$(document).on('click', '#page-title .page-link-two', function (e) {
    e.preventDefault(); // Ngăn chặn hành vi mặc định của liên kết
    var url = $(this).attr('href');
    var page = url.split('page=')[1];
    var id = $('#use-id-count-title').val();
    show_title(id, page); // Gọi hàm show_image với các tham số id và page
});


function show_title(id, page) {
    var formData = new FormData(); // Khởi tạo FormData bên trong hàm
    formData.append('id', id);
    formData.append('page', page);
    formData.append('current_date_old', $('#input-date-upload-old').val());
    formData.append('current_date_new', $('#input-date-upload-new').val());
    formData.append('action', 'show-title');
    let host = window.location.host;
    let protocol = window.location.protocol;

    $.ajax({
        url: `${protocol}//${host}/count-data/`,
        type: 'POST',
        headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            if (response.success === true) {
                $('#use-count-title').empty();
                $('#use-count-title').html(response.title_html);
                $('#page-title').empty();
                $('#page-title').html(response.page_bar_html);
            }
        },
        error: function (error) {
            console.log(error);
        }
    });
}