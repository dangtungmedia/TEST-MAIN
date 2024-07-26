document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded with JavaScript');
    get_video_render(1);
    createWebSocket()
    $('#channel_name').change(function () {
        get_video_render(1);
    });

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Hàm để lấy SVG logo dựa trên trạng thái
    function show_video(video, count) {
        const tr = document.createElement('tr');
        tr.className = 'align-middle';
        tr.setAttribute('data-id', video.id);
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
                <label class="col-form-label id-title-video" data-id="${video.id}">${video.title}</label>
                <div>
                    <button class="btn btn-outline-primary btn-play-video" type="button" data-id="${video.id}" data-url="${video.url_video}" data-coreui-toggle="modal" data-coreui-target="#modal-watch-video">
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
                    <button class="btn btn-outline-primary bg-secondary" type="button" data-id="${video.id}">
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

                // Hiển thị video từ dữ liệu nhận được
                data.results.forEach((item, i) => {
                    show_video(item, i + 1);
                });
                show_page_bar(page, data);
                updateStatus();
            })
            .catch(error => console.error('Error:', error));
    }
    // Xử lý sự kiện click vào nút xem thông tin kênh

    // xử lý sự kiện thêm nhiều video cùng lúc

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


    $("#create_videos_news").click(async function () {
        console.log('Create videos');
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
                console.log(data);

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
    // xử lý sự kiện thêm 1 video   

    // Xử lý sự kiện click vào nút xem video
    // Xử lý sự kiện click vào nút sửa video

    $(document).on('click', '.btn-edit', function () {
        var id = $(this).data('id');
        show_infor_video(id);
        $("#input-Thumnail").val('');
        $("#save-text-video").css('display', 'none');
        $('#button-back').css('display', 'none');
        $('#next-cread-image').css('display', 'block');
        $('#button-back-2').css('display', 'none');
        $('#edit_video').css('display', 'none');
        $('#edit_text_video').css('display', 'none');
        $('#input-infor-video').css('display', 'flex');
        $('#input-image-and-text').css('display', 'none');

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
                $('#url-audio').val(data.url_audio);
                $('#url-srt').val(data.url_subtitle);

                $('#inputAudio').val('');
                $('#inputSrt').val('');

                FileUpload();
                edit_text_video(data);
                show_modal_image(data);

            })
            .catch(error => console.error('Error:', error));
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

        // Kiểm tra nếu data.video_image là chuỗi và có thể phân tích cú pháp JSON
        if (typeof data.video_image === 'string') {
            try {
                images = JSON.parse(data.video_image);
                console.log('Parsed JSON data.video_image:', images);
            } catch (e) {
                console.error('Error parsing JSON:', e);
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
        const fetchUrl = `${protocol}//${host}/render-video/${id_video}/update_video/`;
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
                    updateStatus();
                } else {
                    alert(response.message);
                    updateStatus();
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
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



    // Xử lý sự kiện click vào nút render video
    $(document).on('click', '.btn-render', function () {
        var id = $(this).data('id');
        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const fetchUrl = `${protocol}//${host}/render/`;

        var formData = new FormData();
        formData.append('id-video-render', id);
        formData.append('action', 'render-video');

        $.ajax({
            url: fetchUrl,
            type: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success === true) {
                    updateStatus();
                } else {
                    alert(response.message);
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    });

    // Xử lý sự kiện click vào nút upload lại

    // Xử lý sự kiện click vào nút xóa video

    // Web Socket
    // Tạo kết nối với Web Socket

    $(document).on('click', '.btn-play-video', function () {
        let iframe = document.getElementById('videoIframe');
        const videoUrl = this.getAttribute('data-url');
        iframe.src = videoUrl;
    });


    // dừng play video xem thử
    $(document).on('click', '.btn-close-play-video', function () {
        let iframe = document.getElementById('videoIframe');
        iframe.src = '';
    });

    function createWebSocket() {
        var socket = new WebSocket('ws://' + window.location.host + '/ws/update_status/');
        socket.onopen = function () {
            console.log("WebSocket is open now.");
        };
        socket.onmessage = function (e) {
            console.log('Message:', e.data);
            updateStatus();
        }

    }
    // Cập NHập Trạng Thái của Web Socket
    function updateStatus() {
        var ID_VIDEOS = document.querySelectorAll('.align-middle');
        var list_video = [];
        ID_VIDEOS.forEach(item => {
            const url_video = item.getAttribute('data-id');
            list_video.push(url_video);
        });
        const host = window.location.host;
        const protocol = window.location.protocol;
        const csrfToken = getCSRFToken();
        const fetchUrl = `${protocol}//${host}/render-video/status/`;
        var formData = new FormData();
        formData.append('list_video', list_video);
        $.ajax({
            url: fetchUrl,
            type: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success === true) {
                    const data = response.data;
                    console.log('Update status');
                    $("#count-data").empty();
                    $("#count-data").html(response.text);
                    data.forEach(item => {
                        const thumbnailUrl = item.url_thumbnail ? item.url_thumbnail : '/static/assets/img/no-image-available.png';
                        var image = $('img.id-thumbnail-video[data-id="' + item.id + '"]');
                        image.attr('src', thumbnailUrl);

                        $('div.btn-play-video[data-id="' + item.id + '"]');
                        $('div.btn-play-video[data-id="' + item.url_video + '"]');

                        // Check if the item has a URL for the video
                        if (item.url_video === '') {
                            // Disable the button if no video URL is present
                            $('div.btn-render[data-id="' + item.id + '"]').attr('disabled', true);
                        } else {
                            // Enable the button if a video URL is present
                            $('div.btn-render[data-id="' + item.id + '"]').attr('disabled', false);
                        }

                        var title = $('label.id-title-video[data-id="' + item.id + '"]');
                        title.text(item.title);

                        var status = $('div.status-video[data-id="' + item.id + '"]');
                        status.text(item.status_video);
                        change_color_status();

                        var timeUpload = $('label.time-upload-video[data-id="' + item.id + '"]');
                        timeUpload.text('Ngày Upload ' + item.date_upload + ' Giờ Upload ' + item.time_upload);
                    });

                } else {
                    alert(response.message);
                }
            },
            error: function (error) {
                console.log(error);
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
});