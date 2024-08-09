document.addEventListener('DOMContentLoaded', function () {


    var hasFileLoaded = false;
    var shouldRun = false;

    $('#btn-click-input-video').click(function () {
        $('#input-video-get-text').click();
    });

    $('#input-video-get-text').change(function () {
        var file = $(this)[0].files[0];
        var fileReader = new FileReader();
        fileReader.onload = function (e) {
            var video = document.getElementById('videoPlay');
            video.src = e.target.result;
            video.onloadedmetadata = function () {
                var duration = formatDuration(video.duration);
                $('#video-duration').text('00:00:00.0/' + duration);
                $('#video-show').show();
                $('#setting-get-text-video').show();
                if (!hasFileLoaded) {
                    get_position_video();
                    hasFileLoaded = true;
                }
            }
        }
        fileReader.readAsDataURL(file);
    });

    $('#btn-reset-video').click(function () {
        var video = document.getElementById('videoPlay');
        video.currentTime = 0;
    });


    function formatDuration(duration) {
        var hours = Math.floor(duration / 3600);
        var minutes = Math.floor((duration - (hours * 3600)) / 60);
        var seconds = duration - (hours * 3600) - (minutes * 60);
        var milliseconds = (seconds - Math.floor(seconds)).toFixed(1).slice(2);

        hours = (hours < 10) ? "0" + hours : hours;
        minutes = (minutes < 10) ? "0" + minutes : minutes;
        seconds = (seconds < 10) ? "0" + Math.floor(seconds) : Math.floor(seconds);

        return hours + ':' + minutes + ':' + seconds + '.' + milliseconds;
    }

    function get_position_video() {
        var videoShowElement = document.getElementById('video-show');

        var topPosition = videoShowElement.offsetTop + 520; // Cộng thêm 520 vào vị trí top
        var leftPosition = videoShowElement.offsetLeft;

        var canvasElement = document.getElementById('canvas');
        canvasElement.style.top = topPosition + 'px';
        canvasElement.style.left = leftPosition + 'px';
        canvasElement.style.width = '1280px';
        canvasElement.style.height = '200px';

        var htmlToAdd = `
            <div class="drag-resize-item-active draggable resizable drag-resize-item" 
                style="position: absolute; top: ${topPosition}px; left: ${leftPosition}px; width: 1280px; height: 200px; z-index: auto;">
                <div class="handle handle-tl" style="display: block;"></div>
                <div class="handle handle-tm" style="display: block;"></div>
                <div class="handle handle-tr" style="display: block;"></div>
                <div class="handle handle-mr" style="display: block;"></div>
                <div class="handle handle-br" style="display: block;"></div>
                <div class="handle handle-bm" style="display: block;"></div>
                <div class="handle handle-bl" style="display: block;"></div>
                <div class="handle handle-ml" style="display: block;"></div>
            </div>
        `;
        videoShowElement.insertAdjacentHTML('beforeend', htmlToAdd);
        setting_draw();
    }

    function setting_draw() {
        const restrictElement = document.getElementById('videoPlay');
        var canvasElement = document.getElementById('canvas');

        interact('.draggable')
            .draggable({
                inertia: true,
                autoScroll: true,
                modifiers: [
                    interact.modifiers.restrictRect({
                        restriction: restrictElement,
                        endOnly: false
                    })
                ],
                listeners: {
                    move: function (event) {
                        let target = event.target;
                        let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;
                        let y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy;

                        // Di chuyển phần tử
                        target.style.transform = `translate(${x}px, ${y}px)`;
                        target.setAttribute('data-x', x);
                        target.setAttribute('data-y', y);

                        // Di chuyển canvasElement cùng phần tử
                        canvasElement.style.transform = `translate(${x}px, ${y}px)`;
                        canvasElement.setAttribute('data-x', x);
                        canvasElement.setAttribute('data-y', y);
                    }
                }
            })
            .resizable({
                edges: {
                    left: '.handle-tl, .handle-ml, .handle-bl',
                    right: '.handle-tr, .handle-mr, .handle-br',
                    top: '.handle-tl, .handle-tm, .handle-tr',
                    bottom: '.handle-bl, .handle-bm, .handle-br'
                },
                modifiers: [
                    interact.modifiers.restrictEdges({
                        outer: restrictElement,
                        endOnly: false
                    })
                ],
                listeners: {
                    move: function (event) {
                        let target = event.target;

                        // Tính toán kích thước mới
                        let newWidth = event.rect.width;
                        let newHeight = event.rect.height;

                        // Cập nhật kích thước của phần tử
                        target.style.width = newWidth + 'px';
                        target.style.height = newHeight + 'px';

                        // Cập nhật kích thước của canvasElement
                        canvasElement.style.width = newWidth + 'px';
                        canvasElement.style.height = newHeight + 'px';

                        // Cập nhật vị trí phần tử
                        let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.deltaRect.left;
                        let y = (parseFloat(target.getAttribute('data-y')) || 0) + event.deltaRect.top;

                        target.style.transform = `translate(${x}px, ${y}px)`;
                        target.setAttribute('data-x', x);
                        target.setAttribute('data-y', y);

                        // Cập nhật vị trí canvasElement
                        canvasElement.style.transform = `translate(${x}px, ${y}px)`;
                        canvasElement.setAttribute('data-x', x);
                        canvasElement.setAttribute('data-y', y);
                    }
                }
            });
    }

    var video = document.getElementById('videoPlay');
    // Listen for the timeupdate event on the video element

    video.addEventListener('timeupdate', function () {
        // Format the current time and total duration of the video
        var currentTime = formatDuration(video.currentTime);
        var duration = formatDuration(video.duration);

        // Update the text of the video-duration element
        $('#video-duration').text(currentTime + '/' + duration);
    });

    video.addEventListener('ended', function () {
        shouldRun = false;
        $('#btn-auto-get-text').removeClass('btn-danger').addClass('btn-info');
        $('#btn-auto-get-text').text('AUTO');
    });


    function next_time_video() {
        var video = document.getElementById('videoPlay');
        var count = parseFloat($('#input-count-next').val());
        video.currentTime = video.currentTime + count;
    }

    function left_time_video() {
        var video = document.getElementById('videoPlay');
        var count = parseFloat($('#input-count-next').val());
        video.currentTime = video.currentTime - count;
    }

    $(document).keydown(function (e) {
        if (e.keyCode == 37) {
            left_time_video();
        } else if (e.keyCode == 39) {
            next_time_video();
        }
    });


    $('#btn-left-video').click(function () {
        left_time_video()
    });

    $('#btn-next-video').click(function () {
        next_time_video()
    });


    $('#btn-reset-video').click(function () {
        var video = document.getElementById('videoPlay');
        video.currentTime = 0;
    });


    $('#btn-play-video').click(function () {
        var video = document.getElementById('videoPlay');
        if (video.paused) {
            video.play();
            $('#logo-svg-play-video').attr('xlink:href', '/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-pause');
        } else {
            video.pause();
            $('#logo-svg-play-video').attr('xlink:href', '/static/assets/vendors/@coreui/icons/svg/free.svg#cil-media-play');
        }
    });


    socket = new WebSocket('ws://' + window.location.host + '/ws/update_status/');

    socket.onopen = function (e) {
        console.log('WebSocket is open now.');
    };

    socket.onmessage = function (event) {
        var data = JSON.parse(event.data);
        if (data.status === 'get_text_video') {
            alert(data.text);
        }
    };

    document.getElementById('btn-get-text').addEventListener('click', function () {
        var video = document.getElementById('videoPlay');
        var canvas = document.getElementById('canvas');
        var ctx = canvas.getContext('2d');
        document.getElementById('text-video').value = '';
        if (video.src.startsWith('http')) {
            // Đảm bảo rằng video từ URL hỗ trợ CORS
            video.crossOrigin = 'anonymous';
        }
        var videoRect = video.getBoundingClientRect();
        var canvasRect = canvas.getBoundingClientRect();

        var sourceX = (canvasRect.left - videoRect.left) * (video.videoWidth / videoRect.width);
        var sourceY = (canvasRect.top - videoRect.top) * (video.videoHeight / videoRect.height);
        var sourceWidth = canvasRect.width * (video.videoWidth / videoRect.width);
        var sourceHeight = canvasRect.height * (video.videoHeight / videoRect.height);

        // Đảm bảo rằng sourceWidth và sourceHeight không vượt quá kích thước của video
        if (sourceX + sourceWidth > video.videoWidth) {
            sourceWidth = video.videoWidth - sourceX;
        }
        if (sourceY + sourceHeight > video.videoHeight) {
            sourceHeight = video.videoHeight - sourceY;
        }

        // Điều chỉnh kích thước canvas để phù hợp với kích thước cắt
        canvas.width = sourceWidth;
        canvas.height = sourceHeight;

        ctx.drawImage(video, sourceX, sourceY, sourceWidth, sourceHeight, 0, 0, sourceWidth, sourceHeight);

        // Convert canvas to Blob and send via WebSocket
        canvas.toBlob(function (blob) {
            var reader = new FileReader();
            reader.onloadend = function () {
                var base64data = reader.result.replace(/^data:image\/(png|jpg);base64,/, "");

                var KEY_API_GOOGLE = "AIzaSyDNoZlY0D2a2xXxVfyAIXBMHsKZpqfd4YM";

                var url = `https://vision.googleapis.com/v1/images:annotate?key=${KEY_API_GOOGLE}`;

                var request_data = {
                    "requests": [
                        {
                            "image": {
                                "content": base64data
                            },
                            "features": [
                                {
                                    "type": "TEXT_DETECTION"
                                }
                            ]
                        }
                    ]
                };

                fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(request_data)
                })
                    .then(response => response.json())
                    .then(data => {
                        var text = data.responses[0].fullTextAnnotation.text;
                        document.getElementById('text-video').value = text;
                    })
                    .catch(error => {
                        console.error("Error:", error);
                    });
            };
            reader.readAsDataURL(blob);
        }, 'image/png');
    });

    socket.onmessage = function (event) {
        let data;
        try {
            data = JSON.parse(event.data);
            console.log('Received:', data);

            if (data.message === 'get-text-video') {
                document.getElementById('text-video').value = data.data;
            }
        }
        catch (e) {
            console.error(e);
            return;
        }
    }





    $('#btn-save-text').click(function () {
        sever_Text()
    });

    function sever_Text() {
        var text = document.getElementById('text-video').value;
        if (text == '') {
            return;
        }

        var textArea = document.getElementById('text-all-video');
        var allText = textArea.value.split('\n \n'); // Tách các đoạn văn bản thành mảng
        var recentText = allText.slice(-300); // Lấy khoảng 300 đoạn văn bản cuối
        $('#text-video').val('');

        if (recentText.includes(text)) {
            return; // Nếu đoạn văn bản đã tồn tại, không lưu
        }

        textArea.value += text + '\n \n';
    }

    $('#input-size').change(function () {
        var size = $(this).val();
        var textElement = document.getElementById('text-video');
        textElement.style.fontSize = size + 'px';
    });
});