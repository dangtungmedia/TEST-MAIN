document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded with JavaScript');

    const successOutlined = document.getElementById('success-outlined');
    const dangerOutlined = document.getElementById('danger-outlined');

    document.getElementById("btn-add-text-content").style.display = "none";
    document.getElementById("add-videos").style.display = "none";
    document.getElementById("btn-add-url-videos").style.display = "none";
    document.getElementById("btn-render-all").style.display = "none";
    document.getElementById("btn-render-erron").style.display = "none";
    document.getElementById("btn-upload-erron").style.display = "none";

    document.getElementById("btn-add-video").style.display = "block";

    if (successOutlined) {
        

        successOutlined.addEventListener('change', function () {
            if (this.checked) {
                GetFolderSelected(true);
            }
        });
    }

    if (dangerOutlined) {
        dangerOutlined.addEventListener('change', function () {
            if (this.checked) {
                GetFolderSelected(false);
            }
        });
    }

    get_video_render(1);

    $('#folder_name').change(function () {
        GetProfileSelected();
    });

    $('#channel_name').change(function () {
        get_video_render(1);
    });

    let socket;
    let reconnectInterval = 5000; // Thời gian chờ trước khi thử kết nối lại (ms)
    let messageQueue = []; // Hàng đợi để lưu trữ tất cả các tin nhắn

    function initializeWebSocket() {
        socket = new WebSocket('ws://' + window.location.host + '/ws/update_status/');

        socket.onopen = function () {
            console.log('WebSocket connection opened.');

            // Gửi lại tất cả các tin nhắn trong hàng đợi nếu có
            while (messageQueue.length > 0) {
                const message = messageQueue.shift();
                socket.send(message);
            }

            // Lấy danh sách video và thông tin người dùng
            var list_video = [];
            var ID_VIDEOS = document.querySelectorAll('.video');
            ID_VIDEOS.forEach(item => {
                const url_video = item.getAttribute('data-id');
                list_video.push(url_video);
            });

            var userElement = document.getElementById('user-id');
            var userId = userElement.getAttribute('data-id');

            const identifyMessage = JSON.stringify({
                type: 'identify',
                user_id: userId
            });
            socket.send(identifyMessage);
        };

        socket.onmessage = function (event) {
            let data;
            try {
                data = JSON.parse(event.data);
                console.log('Received:', data);

                if (!data.message) {
                    console.error('Received message without type:', data);
                    return;
                }
                // Xử lý các loại thông điệp khác nhau
                if (data.message === 'update_status') {
                    updateVideoRender(data.data);
                } else if (data.message === 'update_count') {
                    $('#count-data').html(data.data);
                } else if (data.message === 'btn-edit') {
                    show_infor_video(data.data);
                } else if (data.message === 'add-one-video') {
                    add_one_video_web(data.data);
                    show_infor_video(data.data);
                    $('#next-cread-image').click();

                } else if (data.message === 'add-text-folder') {
                    if (data.success === true) {
                        alert(data.message);
                        $('#input-url-channel-folder').val('');
                        $('#exampleFormControlTextarea1').val('');
                    } else {
                        alert(data.message);
                    }
                } else if (data.message === 'btn-delete') {
                    if (data.data.success === true) {
                        var id = data.data.id_video;
                        $('tr.align-middle[data-id="' + id + '"]').remove();
                    } else {
                        alert(data.data.message);
                    }
                } else if (data.message === 'btn-play-video') {
                    console.log('Play video:', data);
                    let videoUrl = data.data; // URL của video
                    let fullUrl = window.location.protocol + '//' + window.location.host + videoUrl; // Tạo URL đầy đủ
                    console.log('Full URL:', fullUrl); // Sử dụng console.log để in ra URL đầy đủ
                    window.open(fullUrl, '_blank'); // Mở URL trong tab mới
                }

            } catch (error) {
                console.error('Error parsing JSON:', error);
                console.error('Received data:', event.data);
            }
        };

        socket.onclose = function (event) {
            console.log('WebSocket is closed now. Attempting to reconnect...');
            setTimeout(initializeWebSocket, reconnectInterval); // Tự động kết nối lại sau 5 giây
        };

        socket.onerror = function (error) {
            console.error('WebSocket error:', error);
        };
    }

    // Hàm để gửi tin nhắn và lưu vào hàng đợi nếu cần thiết
    function sendMessage(message) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(message);
        } else {
            messageQueue.push(message);
        }
    }

    // Khởi tạo kết nối WebSocket khi trang được tải
    window.onload = function () {
        initializeWebSocket();
    };
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    function checkButtonStatus() {
        const contentSelected = document.getElementById('success-outlined').checked;
        const reupSelected = document.getElementById('danger-outlined').checked;
    
        if (contentSelected) {
            console.log("Content selected:", true);
            return true;
        } else if (reupSelected) {
            console.log("Reup-Video selected:", false);
            return false;
        }
    }


    // Hàm để lấy SVG logo dựa trên trạng thái
    function show_video(video) {
        const tr = document.createElement('tr');
        tr.className = 'align-middle';
        tr.setAttribute('data-id', video.id);

        
        const is_content = checkButtonStatus();
        let show_tittel = "";

        if (is_content === true) {
            show_tittel = video.title;
        } else {
            // Sửa điều kiện kiểm tra
            if (video.url_reupload === null || video.url_reupload === false && video.title !== "") {
                show_tittel = video.title;
            } else {
                show_tittel = video.url_video_youtube;
            }
        }

        const thumbnailUrl = video.url_thumbnail ? video.url_thumbnail : '/static/assets/img/no-image-available.png';

        function getLogoByStatus(status) {
            if (status.includes('Đang chờ render video!') || status.includes('Đang Render')) {
                return `
                    <svg class="icon bg-warring">
                        <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-pause"></use>
                    </svg>
                `;
            } else if (status.includes('Render') || status.includes('Render Thành Công') ||
                status.includes('Đang Upload Lên VPS') || status.includes('Upload VPS Thành Công') ||
                status.includes('Upload Lỗi')) {
                return `
                    <svg class="icon bg-green">
                        <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-play"></use>
                    </svg>
                `;
            } else {
                return `
                    <svg class="icon bg-default">
                        <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-play"></use>
                    </svg>
                `;
            }
        }
        tr.innerHTML = `
            <td class="col-auto gap-0" style="width:40px; padding-left:1rem;">
                <label class="col-form-label">${video.id}</label>
            </td>
            <th class="col-auto">
                <img class="id-thumbnail-video" data-id="${video.id}" src="${thumbnailUrl}" style="height: 75px; width:133px; border-radius: 5px; border: 2px solid rgb(255, 132, 0);" onerror="this.onerror=null; this.src='/static/assets/img/no-image-available.png';">
            </th>
            <td class="col">
                <label class="col-form-label id-title-video" data-id="${video.id}">${show_tittel}</label>
                <div>
                    <button class="btn btn-outline-primary btn-play-video" style="background-color: #38b2ac;" type="button" data-id="${video.id}" data-url="${video.url_video}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-airplay"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-edit bg-warning" type="button" data-id="${video.id}" data-coreui-toggle="modal" data-coreui-target="#modal-infor-video">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-pencil"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-render  bg-success" type="button" data-id="${video.id}">
                        ${getLogoByStatus(video.status_video)}
                    </button>
                    <button class="btn btn-outline-primary bg-secondary btn-re-upload" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-reload"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary bg-info" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-arrow-thick-from-bottom"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-delete bg-danger" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-trash"></use>
                        </svg>
                    </button>
                    <label class="col-form-label time-upload-video" data-id="${video.id}">Ngày Upload ${video.date_upload} Giờ Upload ${video.time_upload}</label>
                </div>
            </td>
            <td class="col text-center">
                <div class="col-form-label status-video" style="width:300px;"data-id="${video.id}">
                    ${video.status_video}

                </div>
            </td>
            <td class="col text-center">
                <div class="col-form-label">${video.name_video}</div>
            </td>
            <td class="col text-center">
                <label class="col-form-label">${video.timenow}</label>
            </td>
        `;
        document.getElementById("myTbody").appendChild(tr);
        change_color_status();
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
                // Kiểm tra dữ liệu trả về
                if (!data.results || !Array.isArray(data.results)) {
                    throw new Error('Invalid data format: results not found or not an array');
                }

                // Xóa nội dung hiện tại
                document.getElementById("myTbody").innerHTML = "";
                document.getElementById("page_bar").innerHTML = "";

                time_upload = data.results[0]['profile_id']['channel_time_upload']

                document.getElementById("input-time-upload_channel").value = time_upload;
                document.getElementById("input-time-model-url").value = time_upload;

                // Hiển thị video từ dữ liệu nhận được
                data.results.forEach((item, i) => {
                    show_video(item);
                });
                show_page_bar(page, data);
            })
            .catch(error => console.error('Error:', error));
    }

    function add_one_video_web(video) {
        const tr = document.createElement('tr');
        tr.className = 'align-middle';
        tr.setAttribute('data-id', video.id);
        const thumbnailUrl = video.url_thumbnail ? video.url_thumbnail : '/static/assets/img/no-image-available.png';

        
        const is_content = checkButtonStatus();
        let show_tittel = "";

        if (is_content === true) {
            show_tittel = video.title;
        } else {
            // Sửa điều kiện kiểm tra
            if (video.url_reupload === null || video.url_reupload === false && video.title !== "") {
                show_tittel = video.title;
            } else {
                show_tittel = video.url_video_youtube;
            }
        }



        function getLogoByStatus(status) {
            if (status.includes('Đang chờ render video!') || status.includes('Đang Render')) {
                return `
                    <svg class="icon bg-warring">
                        <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-pause"></use>
                    </svg>
                `;
            } else if (status.includes('Render') || status.includes('Render Thành Công') ||
                status.includes('Đang Upload Lên VPS') || status.includes('Upload VPS Thành Công') ||
                status.includes('Upload Lỗi')) {
                return `
                    <svg class="icon bg-green">
                        <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-play"></use>
                    </svg>
                `;
            } else {
                return `
                    <svg class="icon bg-default">
                        <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-play"></use>
                    </svg>
                `;
            }
        }

        tr.innerHTML = `
            <td class="col-auto gap-0" style="width:40px; padding-left:1rem;">
                <label class="col-form-label">${video.id}</label>
            </td>
            <th class="col-auto">
                <img class="id-thumbnail-video" data-id="${video.id}" src="${thumbnailUrl}" style="height: 75px; width:133px; border-radius: 5px; border: 2px solid rgb(255, 132, 0);" onerror="this.onerror=null; this.src='/static/assets/img/no-image-available.png';">
            </th>
            <td class="col">
                <label class="col-form-label id-title-video" data-id="${video.id}">${show_tittel}</label>
                <div>
                    <button class="btn btn-outline-primary btn-play-video" style="background-color: #38b2ac;" type="button" data-id="${video.id}" data-url="${video.url_video}" data-coreui-toggle="modal" data-coreui-target="#modal-watch-video">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-airplay"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-edit bg-warning" type="button" data-id="${video.id}" data-coreui-toggle="modal" data-coreui-target="#modal-infor-video">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-pencil"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-render  bg-success" type="button" data-id="${video.id}">
                        ${getLogoByStatus(video.status_video)}
                    </button>
                    <button class="btn btn-outline-primary bg-secondary btn-re-upload" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-reload"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary bg-info" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-arrow-thick-from-bottom"></use>
                        </svg>
                    </button>
                    <button class="btn btn-outline-primary btn-delete bg-danger" type="button" data-id="${video.id}">
                        <svg class="icon">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-trash"></use>
                        </svg>
                    </button>
                    <label class="col-form-label time-upload-video" data-id="${video.id}">Ngày Upload ${video.date_upload} Giờ Upload ${video.time_upload}</label>
                </div>
            </td>
            <td class="col text-center">
                <div class="col-form-label status-video" style="width:300px;" data-id="${video.id}">
                    ${video.status_video}
                </div>
            </td>
            <td class="col text-center">
                <div class="col-form-label">${video.name_video}</div>
            </td>
            <td class="col text-center">
                <label class="col-form-label">${video.timenow}</label>
            </td>
        `;

        const myTbody = document.getElementById("myTbody");
        if (myTbody.firstChild) {
            myTbody.insertBefore(tr, myTbody.firstChild);
        } else {
            myTbody.appendChild(tr);
        }

        change_color_status();
    }

    $('#add-videos').click(function () {
        console.log('Add videos');
        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const fetchUrl = `${protocol}//${host}/profiles/${$('#channel_name').val()}/`;
        console.log(fetchUrl);
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
                console.log(data);
                $('#input-time-upload').val(data.channel_time_upload);
            })
            .catch(error => console.error('Error:', error));
    });

    
    // xử lý sự kiện thêm 1 video   
    // Xử lý sự kiện click vào nút sửa video

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
        if ($('#id-video-edit').val() === '') {
            cread_one_video()
            $("#input-Thumnail").val('');
        } else {
            $('#input-infor-video').css('display', 'none');
            $('#input-image-and-text').css('display', 'block');
            $('#save-text-video').css('display', 'block');
            $('#next-cread-image').css('display', 'none');
            $('#button-back').css('display', 'block');
            $('#button-back-2').css('display', 'none');
            $('#save-text-video').css('display', 'none');
            $('#edit_video').css('display', 'block');
        }
    });

    // button next khi đã nhập nội dung và audio
    $('#edit_video').click(function () {
        var file_audio = $('#inputAudio')[0].files[0];
        var file_srt = $('#inputSrt')[0].files[0];

        var url_audio = $('#url-audio').val().trim();
        var url_srt = $('#url-srt').val().trim();


        if ((file_audio && !file_srt) || (!file_audio && file_srt)) {
            // Kiểm tra tiếp điều kiện của URL
            if (!url_audio || !url_srt) {
                alert('Vui lòng nhập File URL audio và URL srt');
                return;
            }
        }

        update_text_edit();
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

    $('#input-Thumnail').change(function () {
        var file = $(this)[0].files[0];

        // Tạo một đối tượng FileReader để đọc tệp
        var reader = new FileReader();

        // Đặt hàm xử lý khi FileReader hoàn tất việc đọc tệp
        reader.onload = function (e) {
            // Cập nhật thuộc tính src của thẻ img để hiển thị hình ảnh
            $('#Image-Thumnail-infor-video').attr('src', e.target.result);
        }
        // Đọc tệp hình ảnh dưới dạng URL dữ liệu
        reader.readAsDataURL(file);
    });

    $('#inputAudio').change(function () {
        FileUpload()
    });

    $('#inputSrt').change(function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const content = e.target.result;
                const textContent = extractTextFromSrt(content);
                $('#input-text-content').val(textContent);
            };
            reader.readAsText(file);
        } else {
            alert('Please select a valid SRT file.');
        }
        FileUpload();

    });
    // chuyển đổi file srt thành văn bản 
    function extractTextFromSrt(content) {
        const lines = content.split('\n');
        const textLines = [];
        const timePattern = /^[0-9]+$/; // Pattern to match lines with only numbers

        lines.forEach(line => {
            line = line.trim();
            if (line && !line.match(timePattern) && !line.includes('-->')) {
                textLines.push(line);
            }
        });

        return textLines.join('\n\n');
    }
    // ẩn hiện input file audio và str
    function FileUpload() {
        var file_audio = $('#inputAudio')[0].files[0];
        var file_srt = $('#inputSrt')[0].files[0];
        var url_audio = $('#url-audio').val();
        var url_srt = $('#url-srt').val();

        if (file_audio) {
            $('#url-audio').css('display', 'none');
            $('#inputAudio').css('display', 'block');
        } else {
            if (url_audio) {
                $('#url-audio').css('display', 'block');
                $('#inputAudio').css('display', 'none');
            } else {
                $('#url-audio').css('display', 'none');
                $('#inputAudio').css('display', 'block');
            }
        }
        if (file_srt) {
            $('#url-srt').css('display', 'none');
            $('#inputSrt').css('display', 'block');
        } else {
            if (url_srt) {
                $('#url-srt').css('display', 'block');
                $('#inputSrt').css('display', 'none');
            } else {
                $('#url-srt').css('display', 'none');
                $('#inputSrt').css('display', 'block');
            }
        }

        if (file_audio || file_srt || url_audio || url_srt) {
            var textarea = $('#input-text-content');
            textarea.attr('readonly', 'readonly');
        } else {
            var textarea = $('#input-text-content');
            textarea.removeAttr('readonly');
        }
    }

    $('#btnDeleteFileAudio').click(function () {
        $('#inputAudio').val('');
        $('#url-audio').val('');
        FileUpload()
    });

    $('#btnDeleteFileSrt').click(function () {
        $('#inputSrt').val('');
        $('#url-srt').val('');
        FileUpload()
    });

    $('#btnChangeFileAudio').click(function () {
        $('#inputAudio').click();
    });

    $('#btnChangeFileSrt').click(function () {
        $('#inputSrt').click();
    });
    //chia dòng
    $('#btn-splitText').click(function () {
        var text_content = $('#input-text-content').val();
        var regexPattern = $('#splitText').val();
        var result = subRegex(text_content, regexPattern);
        $('#input-text-content').val(result);
        show_count_text();
    });

    //chia thao ký tự
    $('#btn-splitText-2').click(function () {
        var text_content = $('#input-text-content').val();
        var char = $('#splitText2').val();
        var regexPattern = `(^.{0,100000}[${char}](?!$))(.{0,105000}$)`;

        var result = subRegex(text_content, regexPattern);

        var lines = result.split('\n\n');
        var lineCount = lines.filter(function (line) {
            return line.trim() !== ''; // Loại bỏ các dòng trống
        });
        $('#input-text-content').val(lineCount.join('\n\n'));
        show_count_text();
    });

    //Xóa Ký Tự
    $('#delete-characters').click(function () {
        var text_content = $('#input-text-content').val();
        var char = $('#splitText3').val();
        var regexPattern = new RegExp(`[${char}]`, 'g');
        var result = text_content.replace(regexPattern, "");
        $('#input-text-content').val(result);
    });


    function show_count_text() {
        var text_content = $('#input-text-content').val();
        var count_text = text_content.length;

        // Đếm số dòng
        var lines = text_content.split('\n\n');
        var lineCount = lines.filter(function (line) {
            return line.trim() !== ''; // Loại bỏ các dòng trống
        });

        $('#count-text-content').text('Số Ký Tự ' + count_text + ' --- Số Dòng ' + lineCount.length);
    }

    function subRegex(e, t) {
        var n = new RegExp("" + t, "m");
        if (e.match(n))
            for (e = e.replace(n, "$1\n\n$2"); e.match(n);)
                e = e.replace(n, "$1\n\n$2");
        return e;
    }


    function edit_text_video(data) {
        $("#edit-iteam-video").empty();
        const itemsString = data.text_content_2 || "[]";
        // Chuyển đổi từ chuỗi JSON thành danh sách
        const items = JSON.parse(itemsString);
        items.forEach((item, i) => {
            const tr = document.createElement('tr');
            tr.className = 'iteam-text-video';
            tr.innerHTML = `
                <th class="text-center pt-4 iteam-id" data-id="${item.id}">${item.id}</th>
                <td class="col m-3">
                    <span class='iteam-text' data-id="${item.id}">${item.text}</span>
                </td>
                <td class="text-center">
                    <img class='iteam-video-content' data-id="${item.id}" src="${item.url_video ? item.url_video : '/static/assets/img/no-image-available.png'}" 
                        style="height: 75px; width: 133px; border-radius: 5px; border: 2px solid rgb(255, 132, 0);">
                </td>`;
            document.getElementById("edit-iteam-video").appendChild(tr);
        });
    }

    function show_infor_video(data) {
        console.log('Data:', data);
        $('#id-video-edit').val(data.id);
        $('#Image-Thumnail-infor-video').attr('src', data.url_thumbnail ? data.url_thumbnail : '/static/assets/img/no-image-available.png');
        $('#input-title').val(data.title);
        $('#input-description').val(data.description);
        $('#input-keyword').val(data.keywords);
        $('#input-date-upload').val(data.date_upload);
        $('#input-time-upload').val(data.time_upload);
        $("#input-text-content").val(data.text_content);
        $('#url-audio').val(data.url_audio);
        $('#url-srt').val(data.url_subtitle);
        FileUpload();
        edit_text_video(data);
        show_modal_image(data);
    }


    function update_text_edit() {
        const text_content = $('#input-text-content').val();
        const lines = text_content.split('\n\n');
        const lineCount = lines.filter(function (line) {
            return line.trim() !== ''; // Loại bỏ các dòng trống
        });

        var count = document.querySelectorAll('.iteam-text-video').length;

        if (count > lineCount.length) {
            var i = 0;
            document.querySelectorAll('.iteam-text-video').forEach(function (item) {
                if (i < lineCount.length) {
                    const text = lineCount[i];
                    item.querySelector('.iteam-text').textContent = text;
                    i++;
                } else {
                    item.remove(); // Xóa các phần tử 'iteam-text-video' thừa đi
                }
            });
        } else if (count < lineCount.length) {
            for (let i = count; i < lineCount.length; i++) {
                const item = lineCount[i];
                const tr = document.createElement('tr');
                tr.className = 'iteam-text-video';
                tr.innerHTML = `
                    <th class="text-center pt-4 iteam-id" data-id="${i + 1}">${i + 1}</th>
                    <td class="col m-3">
                        <span class='iteam-text' data-id="${i + 1}">${item}</span>
                    </td>
                    <td class="text-center">
                        <img class='iteam-video-content' data-id="${i + 1}" src='/static/assets/img/no-image-available.png'
                            style="height: 75px; width: 133px; border-radius: 5px; border: 2px solid rgb(255, 132, 0);">
                    </td>`;
                document.getElementById("edit-iteam-video").appendChild(tr);
            }
        } else {
            document.querySelectorAll('.iteam-text-video').forEach(function (item, i) {
                const text = lineCount[i];
                item.querySelector('.iteam-text').textContent = text;
            });
        }
    }

    $(document).on('click', '#open-input-image', function () {
        $('#modal-overlay').css('display', 'block');
        $('#iteam-edit').val('none');
    });

    function show_modal_image(data) {
        let images;

        // Kiểm tra nếu data.video_image là null hoặc undefined
        if (data.video_image === null || data.video_image === undefined) {
            images = [];
        } else if (typeof data.video_image === 'string') {
            // Kiểm tra nếu data.video_image là chuỗi và có thể phân tích cú pháp JSON
            try {
                images = JSON.parse(data.video_image);
            } catch (e) {
                images = [];
            }
        } else if (Array.isArray(data.video_image)) {
            images = data.video_image;
        } else {
            images = [];
        }
        // Loại bỏ các phần tử .iteam-image hiện có trước khi thêm mới
        const iteamImageDivs = document.querySelectorAll('.iteam-image');
        iteamImageDivs.forEach(div => div.remove());

        // Duyệt qua từng URL hình ảnh và tạo phần tử tương ứng
        images.forEach(imageUrl => {
            // Tạo phần tử div để chứa nội dung HTML
            const div = document.createElement('div');
            div.className = 'col iteam-image'; // Đảm bảo gán đúng class
            div.setAttribute('data-toggle', 'tick-icon');

            // Lấy tên tệp hình ảnh bằng hàm get_name_image_url
            const fileName = get_name_image_url(imageUrl, 12);

            // Gán nội dung HTML vào div
            div.innerHTML = `
                <div class="card border-success p-1 enlarge-on-hover" style="height: 150px; width: 150px;">
                    <img class="card-img-top file-image-url" style="height: 90px;" src="${imageUrl}" alt="Image">
                    <!-- Icon dấu tích -->
                    <div class="tick-icon">
                        <svg class="icon p-2" style="height: 50px; width: 50px; color: aqua;">
                            <use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-chevron-circle-down-alt"></use>
                        </svg>
                    </div>
                    <div class="progress progress-thin my-2" style="height: 5px;">
                        <div class="progress-bar bg-success" role="progressbar" style="width: 100%" aria-valuenow="25" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                    <ul class="nav justify-content-center">${fileName}</ul>
                </div>
            `;
            // Thêm div mới tạo vào container (giả sử bạn có container với id 'image-video')
            document.getElementById("image-video").appendChild(div);
        });
    }

    function get_name_image_url(url, maxLength) {
        // Decode the URL to handle percent-encoded characters
        const decodedUrl = decodeURIComponent(url);

        // Split the URL by '/' to get the parts
        const parts = decodedUrl.split('/');

        // Get the last part which contains the file name
        const fileNameWithParams = parts[parts.length - 1];

        // Split the file name by '?' to remove parameters
        const fileNameWithoutParams = fileNameWithParams.split('?')[0];

        // Truncate the file name if it's longer than maxLength
        if (fileNameWithoutParams.length > maxLength) {
            const firstPart = fileNameWithoutParams.substring(0, 6); // First 6 characters
            const lastPart = fileNameWithoutParams.substring(fileNameWithoutParams.length - 6); // Last 6 characters
            return `${firstPart}...${lastPart}`;
        } else {
            return fileNameWithoutParams;
        }
    }

    $('.close-modal-input-image').click(function () {
        $('#modal-overlay').css('display', 'none');
    });

    $('#modal-overlay').click(function (event) {
        // Kiểm tra xem phần tử mà sự kiện được kích hoạt có phải là phần nền mờ không
        if (event.target === this) {
            // Phóng to modal một chút
            enlargeModal();
        }
    });

    function enlargeModal() {
        var modalContent = $('#modal-image-content .modal-content');
        // Tăng kích thước modal
        modalContent.css('transform', 'scale(1.1)');
        modalContent.css('transition', 'transform 0.5s ease');

        // Sau 0.5 giây, thu nhỏ modal về kích thước ban đầu
        setTimeout(function () {
            modalContent.css('transform', 'scale(1)');
        }, 500);
    }

    $(document).on('click', '[data-toggle="tick-icon"]', function () {
        // Ẩn tất cả các tick-icon cùng cấp
        $(this).siblings().find('.tick-icon').hide();
        // Hiển thị tick-icon trong cột được click
        $(this).find('.tick-icon').show();
    });

    $(document).on('click', '#check-delete-image', function () {
        // Xóa tất cả các cột đã chọn
        $('[data-toggle="tick-icon"]').siblings().find('.tick-icon').hide();
    });

    $(document).on('change', '#input-image', function () {
        var files = $(this)[0].files;
        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            var newCol = $('<div class="col iteam-image" data-toggle="tick-icon"></div>');
            var newCard = $('<div class="card border-success p-1 enlarge-on-hover" style="height: 150px; width: 150px;"></div>');
            var newTickIcon = $('<div class="tick-icon"></div>');
            var newImage = $('<img class="card-img-top file-image-url" style="height:90px;" src="/static/assets/img/Animation.gif" alt="">');
            var newProgress = $('<div class="progress progress-thin my-2" style="height:5px;"></div>');
            var newProgressBar = $('<div class="progress-bar bg-success" role="progressbar" style="width:0" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>');
            var newSmall = $('<ul class="nav justify-content-center file-image">Đang upload ...</ul>');

            newTickIcon.append('<svg class="icon p-2" style="height: 50px; width: 50px;color: aqua;"><use xlink:href="/static/assets/vendors/@coreui/icons/svg/free.svg#cil-chevron-circle-down-alt"></use></svg>');
            newProgress.append(newProgressBar);
            newCard.append(newImage, newTickIcon, newProgress, newSmall);
            newCol.append(newCard);

            $('.row.row-cols-1.row-cols-md-6.g-3.justify-content-center').prepend(newCol);

            (function (newImage, newSmall, newProgressBar) { // Sử dụng hàm vô danh để bảo vệ giá trị
                var formData = new FormData();
                formData.append('file', file);
                formData.append('id-video-render', $('#id-video-edit').val());
                formData.append('action', 'add-image-video');
                var xhr = new XMLHttpRequest();

                xhr.onload = function () {
                    if (xhr.status === 200) {
                        var response = JSON.parse(xhr.responseText);
                        if (response.success === true) {
                            newImage.attr('src', response.url);
                            var name = get_name_image_url(response.url, 12);
                            newSmall.text(name);

                        } else {
                            console.error('File upload failed.');
                        }
                    } else {
                        console.error('File upload failed.');
                    }
                };

                xhr.upload.onprogress = function (event) {
                    if (event.lengthComputable) {
                        var percentComplete = (event.loaded / event.total) * 100;
                        newProgressBar.css('width', percentComplete + '%');
                        newSmall.text('Đang upload ' + percentComplete.toFixed(0) + '%');
                    }
                };
                const host = window.location.host;
                const protocol = window.location.protocol;
                xhr.open('POST', `${protocol}//${host}/render/`, true);
                xhr.setRequestHeader('X-CSRFToken', document.querySelector('[name=csrfmiddlewaretoken]').value);
                xhr.send(formData);
            })(newImage, newSmall, newProgressBar);
        }
        $('#input-click-image').prependTo('.row.row-cols-1.row-cols-md-6.g-3.justify-content-center');
    });


    $('#delete-image').click(function () {
        // Xóa tất cả các cột chứa ảnh được chọn
        $('[data-toggle="tick-icon"]').each(function () {
            if ($(this).find('.tick-icon').css('display') !== 'none') {
                $(this).remove();
                var imageUrl = $(this).find('.file-image-url').attr('src');
                if (imageUrl === '/static/assets/img/Animation.gif') {
                    return;
                }
                var formData = new FormData();

                formData.append('image_url', imageUrl);
                formData.append('action', 'delete-image-video');
                formData.append('id-video-render', $('#id-video-edit').val());
                const host = window.location.host;
                const protocol = window.location.protocol;
                $.ajax({
                    url: `${protocol}//${host}/render/`,
                    type: 'POST',
                    headers: { 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
                    data: formData,
                    processData: false,
                    contentType: false,
                    success: function (response) {
                        if (response.success === true) {
                            console.log(response);
                        } else {
                            alert(response.message);
                        }
                    },
                    error: function (error) {
                        console.log(error);
                    }
                });

            }
        });
    });


    $(document).on('click', '#random-image', function () {
        var iteam_lines = $('tr.iteam-text-video').length;
        var count_image = parseInt($('#count-image-video').val());
        var images = document.querySelectorAll('.iteam-image');

        if (images.length == 0) {
            alert('không có ảnh nào được chọn');
            return;
        }

        var list_images = [];
        images.forEach(function (image) {
            list_images.push(image.querySelector('.file-image-url').src);
        });

        // Tính toán số lượng hình ảnh và video
        var valueForImages = Math.floor(iteam_lines * (count_image / 100)); // Giá trị cho hình ảnh
        var valueForVideos = iteam_lines - valueForImages; // Giá trị còn lại cho video

        var video = '/static/assets/img/no-image-available.png'; // Đường dẫn đến video mặc định

        // Tạo danh sách ngẫu nhiên các hình ảnh và video
        var selectedImages = getRandomChoices(list_images, valueForImages);
        var selectedVideos = Array(valueForVideos).fill(video);

        // Nối danh sách hình ảnh và video
        var layerContents = selectedImages.concat(selectedVideos);

        // Xáo trộn danh sách layerContents
        layerContents = shuffleArray(layerContents);

        // Đảm bảo không có hai hình ảnh liền kề giống nhau
        layerContents = ensureNoAdjacentDuplicates(layerContents);

        iteam_lines = $('tr.iteam-text-video');
        for (let i = 0; i < iteam_lines.length; i++) {
            const iteam = iteam_lines[i];
            const image = layerContents[i];
            iteam.querySelector('.iteam-video-content').src = image;
        }
    });

    // Hàm xáo trộn mảng
    function shuffleArray(array) {
        for (let i = array.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [array[i], array[j]] = [array[j], array[i]];
        }
        return array;
    }

    // Hàm lấy các phần tử ngẫu nhiên từ một mảng với khả năng trùng lặp
    function getRandomChoices(array, num_elements) {
        let choices = [];
        for (let i = 0; i < num_elements; i++) {
            const randomIndex = Math.floor(Math.random() * array.length);
            choices.push(array[randomIndex]);
        }
        return choices;
    }

    // Hàm đảm bảo không có hai phần tử liền kề giống nhau
    function ensureNoAdjacentDuplicates(array) {
        for (let i = 1; i < array.length; i++) {
            if (array[i] === array[i - 1]) {
                // Tìm phần tử khác để đổi chỗ
                for (let j = i + 1; j < array.length; j++) {
                    if (array[j] !== array[i - 1]) {
                        [array[i], array[j]] = [array[j], array[i]];
                        break;
                    }
                }
            }
        }
        return array;
    }

    $(document).on('click', '.iteam-video-content', function () {
        var id = $(this).data('id');
        $('#iteam-edit').val(id);
        $('#modal-overlay').css('display', 'block');
    });


    $('#choice_image').click(function () {
        var id = $('#iteam-edit').val();
        if (id === 'none') {
            return;
        }
        var image_url = $('.tick-icon:visible').siblings('.file-image-url').attr('src');

        if (image_url === undefined) {
            alert('Vui lòng chọn ảnh');
            return;
        }
        $('img.iteam-video-content[data-id="' + id + '"]').attr('src', image_url);
        $('#check-delete-image').click();
        $('#modal-overlay').css('display', 'none');
    });

    function get_image_iteam() {
        var images = document.querySelectorAll('.iteam-image');
        const image_content = [];
        images.forEach(iteam => {
            const url_video = iteam.querySelector('.file-image-url').src;
            image_content.push(url_video);
        });
        return image_content;
    }


    function get_text_json() {
        let iteam_lines = document.querySelectorAll('.iteam-text-video');
        let text_content = ''; // Sử dụng let để có thể gán lại giá trị sau này.
        let text_content_2 = [];

        iteam_lines.forEach(iteam => {
            let id = iteam.querySelector('.iteam-id').textContent;
            let text = iteam.querySelector('.iteam-text').textContent;
            let url_video = iteam.querySelector('.iteam-video-content').src;
            let host = window.location.host;
            let protocol = window.location.protocol;
            let noImageUrl = `${protocol}//${host}/static/assets/img/no-image-available.png`;

            url_video = (url_video === noImageUrl) ? "" : url_video;
            text_content_2.push({ id: id, text: text, url_video: url_video });
            text_content += text + '\n\n';
        });
        return { text_content: text_content, text_content_2: text_content_2 };
    }

    $(document).on('click', '.btn-play-video', function () {
        var id = $(this).data('id');
        const renderMessage = JSON.stringify({
            type: 'btn-play-video',
            id_video: id,
        });
        sendMessage(renderMessage);


    });

    // dừng play video xem thử
    $(document).on('click', '.btn-close-play-video', function () {
        let iframe = document.getElementById('videoIframe');
        iframe.src = '';
    });


    $(document).on('click', '.btn-render', function () {
        var id = $(this).data('id');
        const renderMessage = JSON.stringify({
            type: 'btn-render',
            id_video: id,
        });
        sendMessage(renderMessage);
    });

    $(document).on('click', '.btn-re-upload', function () {
        var id = $(this).data('id');

        const reUploadMessage = JSON.stringify({
            type: 'btn-re-upload',
            id_video: id,
        });
        sendMessage(reUploadMessage);
    });


    $(document).on('click', '.btn-edit', function () {
        var id = $(this).data('id');
        $('#id-video-edit').val(id);
        show_button_model_infor_video();
        const editMessage = JSON.stringify({
            type: 'edit-video',
            id_video: id,
        });
        sendMessage(editMessage);
    });

    $(document).on('click', '#add-one-video', function () {
        $('#id-video-edit').val('');
        show_button_model_infor_video();
    });

    $(document).on('click', '#save-text-video-conent', function () {

        folder = $('#add-video-text-content').val()
        url = $('#input-url-channel-folder').val()
        text = $('#exampleFormControlTextarea1').val()
        if (folder === '' || url === '') {
            alert('Vui lòng nhập đầy đủ thông tin');
            return;
        }
        const add_text_folder = JSON.stringify({
            type: 'add-text-folder',
            folder: folder,
            url: url,
            text: text,
        });
        sendMessage(add_text_folder);

    });

    $(document).on('click', '#save-text-video', function () {

        var file = $('#input-Thumnail')[0].files[0];
        var id_video = $('#id-video-edit').val();

        var file_audio = $('#inputAudio')[0].files[0];
        var file_srt = $('#inputSrt')[0].files[0];
        var url_audio = $('#url-audio').val().trim();
        var url_srt = $('#url-srt').val().trim();
        if ((file_audio && !file_srt) || (!file_audio && file_srt)) {
            // Kiểm tra tiếp điều kiện của URL
            if (!url_audio || !url_srt) {
                alert('Vui lòng nhập File URL audio và URL srt');
                return;
            }
        }

        $('.btn-close').click();

        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const fetchUrl = `${protocol}//${host}/render-video/${id_video}/update_video_render/`;
        const { text_content, text_content_2 } = get_text_json();
        images = get_image_iteam();
        console.log('Debug information');
        console.log(images);
        var formData = new FormData();
        formData.append('title', $('#input-title').val());
        formData.append('description', $('#input-description').val());
        formData.append('keywords', $('#input-keyword').val());
        formData.append('date_upload', $('#input-date-upload').val());
        formData.append('time_upload', $('#input-time-upload').val());
        formData.append('text_content', text_content);
        formData.append('text_content_2', JSON.stringify(text_content_2));
        formData.append('video_image', JSON.stringify(images));

        if (file) {
            formData.append('file-thumnail', file);
            // Tạo một đối tượng FileReader để đọc tệp
            var reader = new FileReader();

            // Đặt hàm xử lý khi FileReader hoàn tất việc đọc tệp
            reader.onload = function (e) {
                var image = $('img.id-thumbnail-video[data-id="' + id_video + '"]');
                image.attr('src', e.target.result);
            }
            // Đọc tệp hình ảnh dưới dạng URL dữ liệu
            reader.readAsDataURL(file);
        }
        if (file_audio) {
            formData.append('file-audio', file_audio);
        }
        if (file_srt) {
            formData.append('file-srt', file_srt);
        }
        console.log('Debug information');
        console.log($('#id-video-edit').val());
        $.ajax({
            url: fetchUrl,
            type: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success === true) {
                    console.log('Cập nhật video thành công');
                } else {
                    alert(response.message);
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    });


    $(document).on('click', '.btn-delete', function () {
        var id = $(this).data('id');
        var userElement = document.getElementById('user-id');
        var userId = userElement.getAttribute('data-id');
        const deleteMessage = JSON.stringify({
            type: 'btn-delete',
            userId: userId,
            id_video: id,
        });
        sendMessage(deleteMessage);
    });


    $("#create_videos_news").click(async function () {
        const countVideos = parseInt($('#count-video').val());
        let dateValue = $('#date-Input').val();
        const timeValue = $('#input-time-upload').val().split(',');
        const characters = $('#count-text-video').val();

        $('#progress-bar-status').css('width', `${0}%`);
        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const profile_id = $('#channel_name').val();
        const fetchUrl = `${protocol}//${host}/profiles/${profile_id}/add_videos/`;

        $('#progress-bar-status').css('display', 'block'); // Hiển thị thanh tiến trình
        $('#cread-status-videos').text(`Đang tạo video ...1/${countVideos}`);

        let errorOccurred = false;

        for (let i = 0; i < countVideos && !errorOccurred; i++) {
            const date = new Date(dateValue);
            const date_upload_str = date.toISOString().split('T')[0];
            const time = timeValue[i % timeValue.length].trim();
            console.log('Date:', date_upload_str);
            console.log('Time:', time);

            const videoData = {
                upload_time: time,
                upload_date: date_upload_str,
                characters: characters,
            };

            try {
                const response = await fetch(fetchUrl, {
                    method: 'POST',
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(videoData)
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                $('#cread-status-videos').text(`Đang tạo video ...${i + 1}/${countVideos}`);
                const progress = ((i + 1) / countVideos) * 100;
                $('#progress-bar-status').css('width', `${progress}%`);
                $('#progress-bar-status').attr('aria-valuenow', progress);
                if (i + 1 === countVideos) {
                    $('#cread-status-videos').text(`Đã tạo xong ${i + 1} video`);
                }
            } catch (error) {
                console.error('Error:', error);
                $('#cread-status-videos').text(`Lỗi khi tạo video. Đã tạo được ${i} video.`);
                errorOccurred = true; // Đánh dấu lỗi đã xảy ra
            }

            // Kiểm tra nếu đã sử dụng hết tất cả giá trị thời gian upload
            if ((i + 1) % timeValue.length === 0) {
                // Tăng ngày lên 1
                dateValue = new Date(date.setDate(date.getDate() + 1)).toISOString().split('T')[0];
            }
        }

        if (errorOccurred) {
            $('#cread-status-videos').text(`Dừng lại do lỗi. Đã tạo được ${i} video.`);
        }
    });

    $(document).on('click', '#cread-url-videos', async function () {
        var countVideos = countLines(textarea);
        let dateValue = $('#date-Input-url').val();
        let timeValue = $('#input-time-model-url').val().split(',');
        if (countVideos === 0) {
            $('#cread-status-videos').text(`Lỗi : Không có url video`);
            return;
        }else{
            $('#cread-status-videos').text(`Đang tạo video ...1/${countVideos.count}`);
        }

        $('#progress-bar-status').css('width', `${0}%`);

        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const fetchUrl = `${protocol}//${host}/render-video/cread-video-url/`;
        let errorOccurred = false;

        for (let i = 0; i < countVideos.count && !errorOccurred; i++) {
            const date = new Date(dateValue);
            const date_upload_str = date.toISOString().split('T')[0];
            const time = timeValue[i % timeValue.length].trim();

            console.log('Date:', date_upload_str);
            console.log('Time:', time);

            const videoData = {
                upload_time: time,
                upload_date: date_upload_str,
                url_video: countVideos.lines[i].trim(),
                profile_id : $('#channel_name').val(),
                folder_id : $('#folder_name').val()
            };
            try {
                const response = await fetch(fetchUrl, {
                    method: 'POST',  // Đảm bảo phương thức là 'POST'
                    credentials: 'include',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify(videoData)
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                console.log('Kết quả:', data);
                
                add_one_video_web(data.video);
                $('#cread-status-videos').text(`Đang tạo video ...${i + 1}/${countVideos.count}`);
                const progress = ((i + 1) / countVideos.count) * 100;
                $('#progress-bar-status').css('width', `${progress}%`);
                $('#progress-bar-status').attr('aria-valuenow', progress);
                if (i + 1 === countVideos.count) {
                    $('#cread-status-videos').text(`Đã tạo xong ${i + 1} video`);
                }
            } catch (error) {
                console.error('Error:', error);
                $('#cread-status-videos').text(`Lỗi khi tạo video. Đã tạo được ${i} video.`);
                errorOccurred = true; // Đánh dấu lỗi đã xảy ra
            }

            // Kiểm tra nếu đã sử dụng hết tất cả giá trị thời gian upload
            if ((i + 1) % timeValue.length === 0) {
                // Tăng ngày lên 1
                dateValue = new Date(date.setDate(date.getDate() + 1)).toISOString().split('T')[0];
            }
        }
    });

    function show_button_model_infor_video() {
        $('#input-title').val('');
        $('#input-description').val('');
        $('#input-keyword').val('');
        $("#input-Thumnail").val('');
        $('#Image-Thumnail-infor-video').attr('src', '/static/assets/img/no-image-available.png');
        $("#save-text-video").css('display', 'none');
        $('#button-back').css('display', 'none');
        $('#next-cread-image').css('display', 'block');
        $('#button-back-2').css('display', 'none');
        $('#edit_video').css('display', 'none');
        $('#edit_text_video').css('display', 'none');
        $('#input-infor-video').css('display', 'flex');
        $('#input-image-and-text').css('display', 'none');
        $('#inputAudio').val('');
        $('#inputSrt').val('');
    }

    function get_file_image() {
        return new Promise((resolve, reject) => {
            const fileInput = document.getElementById('input-Thumnail');
            const file = fileInput.files[0];

            if (file) {
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function () {
                    const base64Image = reader.result.replace(/^data:image\/(png|jpg|jpeg);base64,/, '');
                    resolve(base64Image);
                };
                reader.onerror = function (error) {
                    console.log('Error: ', error);
                    reject(error);
                };
            } else {
                resolve(null);
            }
        });
    }

    async function cread_one_video() {
        try {
            var userElement = document.getElementById('user-id');
            var userId = userElement.getAttribute('data-id');
            var base64Image = await get_file_image();
            const addOneVideoMessage = JSON.stringify({
                type: 'add-one-video',
                userId: userId,
                profile_id: $('#channel_name').val(),
                title: $('#input-title').val(),
                description: $('#input-description').val(),
                keywords: $('#input-keyword').val(),
                date_upload: $('#input-date-upload').val(),
                time_upload: $('#input-time-upload').val(),
                thumbnail: base64Image // Thêm file ảnh đã mã hóa vào thông điệp JSON
            });
            socket.send(addOneVideoMessage);
        } catch (error) {
            console.log('Error sending WebSocket message: ', error);
        }
    }


    function updateVideoRender(data) {

        const is_content = checkButtonStatus();
        let show_tittel = "";

        if (is_content === true) {
            show_tittel = data.title;
        } else {
            // Sửa điều kiện kiểm tra
            if (data.url_reupload === null || data.url_reupload === false && data.title !== "") {
                show_tittel = data.title;
            } else {
                show_tittel = data.url_video_youtube;
            }
        }
        var ID_VIDEOS = document.querySelectorAll('.align-middle');
        ID_VIDEOS.forEach(item => {
            if (item.getAttribute('data-id') == data.id) {
                const thumbnailUrl = data.url_thumbnail ? data.url_thumbnail : '/static/assets/img/no-image-available.png';
                var image = $('img.id-thumbnail-video[data-id="' + data.id + '"]');
                image.attr('src', thumbnailUrl);

                video_url = $('div.btn-play-video[data-id="' + data.id + '"]');
                // $('div.btn-play-video[data-url="' + data.url_video + '"]');
                video_url.attr('data-url', data.url_video);


                var title = $('label.id-title-video[data-id="' + data.id + '"]');
                title.text(show_tittel);

                var status = $('div.status-video[data-id="' + data.id + '"]');
                status.text(data.status_video);
                change_color_status();

                var timeUpload = $('label.time-upload-video[data-id="' + data.id + '"]');
                timeUpload.text('Ngày Upload ' + data.date_upload + ' Giờ Upload ' + data.time_upload);
            }
        });
    }

    function change_color_status() {
        // Lấy tất cả các phần tử có class "status-video"
        const textstatuss = document.querySelectorAll('.status-video');
        // Duyệt qua từng phần tử
        textstatuss.forEach(textstatus => {
            // Lấy trạng thái văn bản
            const status = textstatus.textContent.trim();

            // Biến để lưu phần đầu và phần còn lại của trạng thái
            let frontPart = '';
            let backPart = '';

            // Tách phần đầu và phần còn lại của trạng thái
            if (status.includes(':')) {
                const parts = status.split(':');
                frontPart = parts[0].trim();
                backPart = parts.slice(1).join(':').trim();
            } else {
                frontPart = status;
            }
            // Tạo phần tử span cho phần đầu và phần còn lại
            const frontSpan = document.createElement('span');
            const backSpan = document.createElement('span');

            frontSpan.textContent = frontPart;
            backSpan.textContent = backPart;

            // Thay đổi màu nền dựa trên trạng thái
            if (frontPart.includes('render')) {
                frontSpan.classList.add('text-info');
            } else if (frontPart.includes('Đang Chờ Render')) {
                frontSpan.classList.add('text-secondary');
            } else if (frontPart.includes('Đang Render')) {
                frontSpan.classList.add('text-warning');
            } else if (frontPart.includes('Render Thành Công') || frontPart.includes('Upload VPS Thành Công')) {
                frontSpan.classList.add('text-success');
            } else if (frontPart.includes('Render Lỗi') || frontPart.includes('Upload Vps Lỗi')) {
                frontSpan.classList.add('text-danger');
            } else if (frontPart.includes('Đang Upload Lên VPS')) {
                frontSpan.classList.add('text-info');
            } else {
                frontSpan.classList.add('text-dark'); // Màu mặc định cho các trạng thái không xác định
            }
            // Thêm các thuộc tính font-weight và font-style
            frontSpan.style.fontWeight = 'bold';
            frontSpan.style.fontStyle = 'italic';

            // Đổi màu phần sau thành màu tím
            backSpan.style.color = 'purple';

            // Xóa nội dung cũ và thêm các phần tử span mới
            textstatus.textContent = '';
            textstatus.appendChild(frontSpan);

            if (backPart) {
                textstatus.appendChild(document.createTextNode(' : ')); // Thêm dấu hai chấm và khoảng trắng
                textstatus.appendChild(backSpan);
            }
        });
    }
    // Lấy Thông Tin Folder Được Chọn


    function GetFolderSelected(is_content) {
        const userElement = document.getElementById('user-id');
        const userId = userElement.getAttribute('data-id');
        // Kiểm tra điều kiện để ẩn hoặc hiện nút
        if (is_content) {
            // Nếu is_content là true, hiển thị nút
            document.getElementById("btn-add-text-content").style.display = "none";
            document.getElementById("add-videos").style.display = "none";
            document.getElementById("btn-add-url-videos").style.display = "none";
            document.getElementById("btn-render-all").style.display = "none";
            document.getElementById("btn-render-erron").style.display = "none";
            document.getElementById("btn-upload-erron").style.display = "none";
            document.getElementById("btn-add-video").style.display = "block";
        } else {
            // Nếu is_content là false, ẩn nút
            document.getElementById("btn-add-text-content").style.display = "inline-block";
            document.getElementById("add-videos").style.display = "inline-block";
            document.getElementById("btn-add-url-videos").style.display = "inline-block";
            document.getElementById("btn-render-all").style.display = "inline-block";
            document.getElementById("btn-render-erron").style.display = "inline-block";
            document.getElementById("btn-upload-erron").style.display = "inline-block";
            document.getElementById("btn-add-video").style.display = "None";
        }

        const host = window.location.host;
        const protocol = window.location.protocol;

        if (!userElement) {
            console.error('User element not found');
            return;
        }

        const url = `${protocol}//${host}/home/folders/get-folders/`;

        const dataToSend = {
            is_content: is_content,
            userId: userId,
        };
        const folderElement = document.getElementById('folder_name');
        if (!folderElement) {
            console.error('Folder name element not found');
            return;
        }

        folderElement.innerHTML = '';
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(dataToSend)
        })
            .then(response => response.json())
            .then(data => {
                data.folders.forEach(folder => {
                    console.log(folder);
                    let option = document.createElement('option');
                    option.value = folder.id;
                    option.text = folder.folder_name; // Assuming 'folder_name' is the field name
                    folderElement.appendChild(option);
                });
                GetProfileSelected();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    }

    function GetProfileSelected() {
        const folderElement = document.getElementById('folder_name');
        const channelElement = document.getElementById('channel_name');
        const host = window.location.host;
        const protocol = window.location.protocol;

        channelElement.innerHTML = '';
        document.getElementById("myTbody").innerHTML = "";
        document.getElementById("page_bar").innerHTML = "";
        if (!folderElement) {
            return;
        }

        if (folderElement.value === '') {
            return;
        }
        console.log('Folder selected:', folderElement.value);

        const folderId = folderElement.value;
        const url = `${protocol}//${host}/home/profiles/by-folder/${folderId}/`;
        console.log(`Fetching data from: ${url}`);

        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                if (!channelElement) {
                    console.error('Channel name element not found');
                    return;
                }
                data.forEach(profile => {
                    console.log(profile);
                    // Tạo tùy chọn cho channelElement
                    let option = document.createElement('option');
                    option.value = profile.id;
                    option.text = profile.channel_name; // Assuming 'channel_name' is the field name
                    channelElement.appendChild(option);
                });
                get_video_render(1);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }


    $("#random-time").click(function () {
        $('#input-time-model-url').val('');
        $('#input-time-model-url').val(generateTimeSlots());
    });

    function generateTimeSlots() {
        var timeSlots = [];
        var list_time = [];
        var count = $('#count-random').val();

        // Tạo danh sách thời gian từ 1 giờ đến 22 giờ với các phút cách nhau là 00, 15, 30 và 45
        for (var hour = 1; hour <= 22; hour++) {
            for (var minute = 0; minute < 60; minute += 15) {
                var formattedHour = hour < 10 ? "0" + hour : hour;
                var formattedMinute = minute < 10 ? "0" + minute : minute;
                timeSlots.push(formattedHour + ":" + formattedMinute);
            }
        }

        // Lấy ngẫu nhiên các thời gian từ danh sách thời gian
        while (list_time.length < count) {
            var randomIndex = Math.floor(Math.random() * timeSlots.length);
            var timeSlot = timeSlots.splice(randomIndex, 1)[0]; // Remove the selected time slot from timeSlots

            list_time.push(timeSlot);
        }

        // Sắp xếp thời gian theo thứ tự tăng dần
        list_time.sort();

        // Chuyển list_time thành chuỗi
        var list_time_string = list_time.join(",");

        return list_time_string;
    }

    $(document).on('click', '#add-url-videos', function () {
        var textarea = document.getElementById('input-url-videos');
        textarea.value = '';
    });

    var textarea = document.getElementById('input-url-videos');
    var urlCountSpan = document.getElementById('url-count');

    // Hàm để đếm số dòng trong textarea
    function countLines(textarea) {
        var lines = textarea.value.split('\n');
        var nonEmptyLines = lines.filter(function(line) {
            return line.trim() !== ''; // Loại bỏ các dòng trống hoặc chỉ chứa khoảng trắng
        });

        // Trả về một đối tượng chứa số dòng không rỗng và chuỗi các dòng không rỗng
        return {
            count: nonEmptyLines.length,
            lines: nonEmptyLines
        };
    }

    // Hàm để cập nhật số dòng hiển thị
    function updateUrlCount() {
        
        var lineCount = countLines(textarea);
        urlCountSpan.innerText = lineCount.count;
    }

    // Gọi hàm updateUrlCount mỗi khi người dùng thay đổi nội dung trong textarea
    textarea.addEventListener('input', updateUrlCount);

    // Khởi tạo giá trị ban đầu khi trang được tải
    updateUrlCount();
});