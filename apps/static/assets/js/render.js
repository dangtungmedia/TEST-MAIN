document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded with JavaScript');
    get_video_render(1);

    $('#channel_name').change(function () {
        get_video_render(1);
    });



    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function show_video(video, count) {
        const tr = document.createElement('tr');
        tr.className = 'align-middle';
        tr.innerHTML = `
            <td class="col-auto gap-0" style="width:40px; padding-left:1rem;">
                <label class="col-form-label">${video.id}</label>
            </td>
            <th class="col-auto">
                <img class="id-thumbnail-video" data-id="${video.id}" src="${video.url_thumbnail}" style="height: 75px; width:133px; border-radius: 5px; border: 2px solid rgb(255, 132, 0);">
            </th>
            <td class="col">
                <label class="col-form-label id-title-video" data-id="${video.id}">${video.title}</label>
                <div>
                    <button class="btn btn-outline-primary" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-airplay"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-edit" type="button" data-id="${video.id}" data-coreui-toggle="modal" data-coreui-target="#modal-infor-video">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-pencil"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-render" type="button" data-id="${video.id}">
                        ${video.status_video.includes('Đang chờ render video!') || video.status_video.includes('Đang Render') ? `
                            <svg class="icon">
                                <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-pause"></use>
                            </svg>
                        ` : `
                            <svg class="icon">
                                <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-play"></use>
                            </svg>
                        `}
                    </button>
                    <button class="btn btn-outline-primary" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-reload"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-arrow-thick-from-bottom"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-delete" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-trash"></use>
                        </svg>
                    </button>
                    <label class="col-form-label time-upload-video">Ngày Upload ${video.date_upload} Giờ Upload ${video.time_upload}</label>
                </div>
            </td>
            <td class="col text-center">
                <div class="col-form-label status-video" data-id="${video.id}">${video.status_video}</div>
            </td>
            <td class="col text-center">
                <div class="col-form-label">${video.name_video}</div>
            </td>
            <td class="col text-center">
                <label class="col-form-label">${video.timenow}</label>
            </td>
        `;
        document.getElementById("myTbody").appendChild(tr);
    }

    function show_page_bar(page, data) {
        const totalPages = Math.ceil(data.count / 50);
        const maxPagesToShow = 3;
        // Tạo thanh phân trang
        const pageBar = document.getElementById("page_bar");

        if (data.previous) {
            const previousLi = document.createElement('li');
            previousLi.className = 'page-item';
            previousLi.innerHTML = `<a class="page-link" href="#" data-page="${page - 1}">Previous</a>`;
            pageBar.appendChild(previousLi);
        } else {
            const previousLi = document.createElement('li');
            previousLi.className = 'page-item disabled';
            previousLi.innerHTML = `<a class="page-link" href="#">Previous</a>`;
            pageBar.appendChild(previousLi);
        }


        // Tạo liên kết số trang
        if (totalPages <= maxPagesToShow + 2) {
            // Hiển thị tất cả các trang nếu tổng số trang nhỏ hơn hoặc bằng maxPagesToShow + 2 (2 cho trang đầu và cuối)
            for (let i = 1; i <= totalPages; i++) {
                const li = document.createElement('li');
                li.className = `page-item ${i === page ? 'active' : ''}`;
                li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
                pageBar.appendChild(li);
            }
        } else {
            // Hiển thị một số trang nếu tổng số trang lớn hơn maxPagesToShow + 2
            const li1 = document.createElement('li');
            li1.className = `page-item ${1 === page ? 'active' : ''}`;
            li1.innerHTML = `<a class="page-link" href="#" data-page="${1}">1</a>`;
            pageBar.appendChild(li1);

            if (page > 3) {
                const liDots = document.createElement('li');
                liDots.className = 'page-item disabled';
                liDots.innerHTML = `<a class="page-link" href="#">...</a>`;
                pageBar.appendChild(liDots);
            }

            const startPage = Math.max(2, page - Math.floor(maxPagesToShow / 2));
            const endPage = Math.min(totalPages - 1, startPage + maxPagesToShow - 1);

            for (let i = startPage; i <= endPage; i++) {
                const li = document.createElement('li');
                li.className = `page-item ${i === page ? 'active' : ''}`;
                li.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
                pageBar.appendChild(li);
            }

            if (page < totalPages - 2) {
                const liDots = document.createElement('li');
                liDots.className = 'page-item disabled';
                liDots.innerHTML = `<a class="page-link" href="#">...</a>`;
                pageBar.appendChild(liDots);
            }

            const liLast = document.createElement('li');
            liLast.className = `page-item ${totalPages === page ? 'active' : ''}`;
            liLast.innerHTML = `<a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>`;
            pageBar.appendChild(liLast);
        }

        if (data.next) {
            const nextLi = document.createElement('li');
            nextLi.className = 'page-item';
            nextLi.innerHTML = `<a class="page-link" href="#" data-page="${page + 1}">Next</a>`;
            pageBar.appendChild(nextLi);
        } else {
            const nextLi = document.createElement('li');
            nextLi.className = 'page-item disabled';
            nextLi.innerHTML = `<a class="page-link" href="#">Next</a>`;
            pageBar.appendChild(nextLi);
        }
        const pageLinks = document.querySelectorAll('.page-link');
        pageLinks.forEach(link => {
            link.addEventListener('click', function (e) {
                e.preventDefault();
                const newPage = parseInt(e.target.getAttribute('data-page'));
                if (newPage >= 1 && newPage <= totalPages) {
                    document.getElementById("myTbody").innerHTML = "";
                    document.getElementById("page_bar").innerHTML = "";
                    get_video_render(newPage);
                }
            });
        });
    }

    function get_video_render(page) {
        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();

        const folderElement = document.getElementById('folder_name');
        const channelElement = document.getElementById('channel_name');
        const folderId = folderElement.value;
        const channelId = channelElement.value;

        const fetchUrl = `${protocol}//${host}/render-video/?page=${page}&profile_id=${channelId}`;

        fetch(fetchUrl, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Data:', data);

                // Kiểm tra dữ liệu trả về
                if (!data.results || !Array.isArray(data.results)) {
                    throw new Error('Invalid data format: results not found or not an array');
                }

                // Xóa nội dung hiện tại
                document.getElementById("myTbody").innerHTML = "";
                document.getElementById("page_bar").innerHTML = "";

                // Hiển thị video từ dữ liệu nhận được
                data.results.forEach((item, i) => {
                    show_video(item, i + 1);
                });
                show_page_bar(page, data);
            })
            .catch(error => console.error('Error:', error));
    }
    // Xử lý sự kiện click vào nút xem thông tin kênh

    // xử lý sự kiện thêm nhiều video cùng lúc

    // xử lý sự kiện thêm 1 video   

    // Xử lý sự kiện click vào nút xem video

    // Xử lý sự kiện click vào nút sửa video

    $(document).on('click', '.btn-edit', function () {
        var id = $(this).data('id');
        show_infor_video(id);
        $("#save-text-video").css('display', 'none');
        $('#button-back').css('display', 'none');
        $('#next-cread-image').css('display', 'block');
        $('#button-back-2').css('display', 'none');
        $('#edit_video').css('display', 'none');
    });

    $("#button-back").click(function () {
        $('#input-infor-video').css('display', 'flex');
        $('#input-image-and-text').css('display', 'none');
        $('#save-text-video').css('display', 'none');
        $('#next-cread-image').css('display', 'block');
        $('#button-back').css('display', 'none');
        $('#button-back2').css('display', 'none');
        $('#edit_video').css('display', 'none');
    });

    $(document).on('click', '#next-cread-image', function () {
        $('#input-infor-video').css('display', 'none');
        $('#input-image-and-text').css('display', 'block');
        $('#save-text-video').css('display', 'block');
        $('#next-cread-image').css('display', 'none');
        $('#button-back').css('display', 'block');
        $('#button-back-2').css('display', 'none');
        $('#save-text-video').css('display', 'none');
        $('#edit_video').css('display', 'block');
    });

    $('#edit_video').click(function () {
        $("#edit_video").css('display', 'none');
        $("#input-image-and-text").css('display', 'none');
        $('#button-back').css('display', 'none');
        $('#edit_text_video').css('display', 'block');
        $('#button-back-2').css('display', 'block');
        $('#save-text-video').css('display', 'block');

    });

    $('#button-back-2').click(function () {
        $('#edit_text_video').css('display', 'none');
        $('#input-image-and-text').css('display', 'block');
        $('#button-back').css('display', 'block');
        $('#edit_video').css('display', 'block');
        $('#button-back-2').css('display', 'none');
        $('#save-text-video').css('display', 'none');
    });

    function show_infor_video(id) {
        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const fetchUrl = `${protocol}//${host}/render-video/${id}/`;

        fetch(fetchUrl, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Data:', data);
                $('#id-video-edit').val(data.id);
                $('#Image-Thumnail-infor-video').attr('src', data.url_thumbnail);
                $('#input-title').val(data.title);
                $('#input-description').val(data.description);
                $('#input-keyword').val(data.keywords);
                $('#input-date-upload').val(data.date_upload);
                $('#input-time-upload').val(data.time_upload);
                $("#input-text-content").val(data.text_content);
            })
            .catch(error => console.error('Error:', error));
    }




    // Xử lý sự kiện click vào nút render video

    // Xử lý sự kiện click vào nút upload lại

    // Xử lý sự kiện click vào nút xóa video

});
