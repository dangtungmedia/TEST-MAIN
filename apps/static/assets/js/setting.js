document.addEventListener('DOMContentLoaded', function () {

    var video_render = 'None'

    function initializeColorPicker(containerId, defaultColor) {
        const colorPickerContainer = document.getElementById(containerId);

        const pickr = Pickr.create({
            el: `#${containerId}`,
            theme: 'nano',
            default: defaultColor,
            components: {
                preview: true,
                opacity: true,
                hue: true,
                interaction: {
                    rgba: false,
                    hsla: false,
                    hsva: false,
                    cmyk: false,
                    input: true,
                    hex: true,
                    clear: false,
                    save: false,
                }
            }
        });

        pickr.on('change', function (color) {
            const hexColor = color.toHEXA().toString();
            colorPickerContainer.style.backgroundColor = hexColor;
            pickr.applyColor();

        });
    }

    ['color-picker-container-1', 'color-picker-container-2', 'color-picker-container-3'].forEach(function (containerId, index) {
        initializeColorPicker(containerId, index === 0 ? 'rgba(44, 56, 74, 0.95)' : 'rgba(255, 255, 255, 0)');
    });

    function toggleVisibility(id, displayValue) {
        var element = document.getElementById(id);
        element.style.display = displayValue;
    }

    function resizer_reup_video() {
        // Lấy phần tử label theo id
        const labelElement = document.getElementById('crop-reup-video');

        // Kiểm tra xem phần tử có tồn tại không
        if (labelElement) {
            // Lấy nội dung từ phần tử
            const labelText = labelElement.textContent;

            // Biểu thức chính quy để trích xuất các giá trị số trong nội dung
            const regex = /\((\d+),(\d+),(\d+),(\d+)\)/;

            // Sử dụng match để tìm các giá trị phù hợp với biểu thức chính quy
            const match = labelText.match(regex);

            // Nếu match không trả về null, lấy các giá trị từ kết quả match
            if (match !== null) {
                const [, topValue, leftValue, widthValue, heightValue] = match.map(Number);
                // Thực hiện các hành động khác dựa trên các giá trị vị trí
                // Ví dụ: Cài đặt các thuộc tính CSS cho một phần tử
                const targetElement = document.getElementById('videoPosition');
                if (targetElement) {
                    targetElement.style.top = `${topValue}px`;
                    targetElement.style.left = `${leftValue}px`;
                    targetElement.style.width = `${widthValue}px`;
                    targetElement.style.height = `${heightValue}px`;
                }
            } else {
                console.log('Không tìm thấy vị trí trong nội dung label.');
            }
        } else {
            console.log('Không tìm thấy phần tử với id "crop-reup-video".');
        }
    }

    function resizer_subtittle_video() {
        const labelElement = document.getElementById('lnB29wbYkZgudKGQ9h9A');
        const targetElement = document.getElementById('videoPosition');
        targetElement.style.top = labelElement.style.top;
        targetElement.style.left = labelElement.style.left;
        targetElement.style.width = labelElement.style.width;
        targetElement.style.height = labelElement.style.height;

    }



    document.getElementById('videoModeSelect').addEventListener('change', function () {
        // Lấy giá trị của option được chọn
        var selectedValue = this.value;
        // Kiểm tra giá trị và thực hiện các hành động tương ứng
        switch (selectedValue) {
            case '1':
                // Thực hiện hành động cho ReupVideo
                toggleVisibility('form-Reup', 'block');
                toggleVisibility('form-Subtitle', 'none');
                toggleVisibility('form-language', 'none');
                toggleVisibility('videoPosition', 'block');
                toggleVisibility('lnB29wbYkZgudKGQ9h9A', 'none');
                toggleVisibility('form-text-Subtitle', 'none');
                video_render = "None";
                resizer_reup_video()
                break;
            case '2':
                // Thực hiện hành động cho Giọng Đọc + Phụ Đề
                toggleVisibility('form-Reup', 'none');
                toggleVisibility('form-Subtitle', 'block');
                toggleVisibility('form-language', 'block');
                toggleVisibility('form-language', 'block');
                toggleVisibility('videoPosition', 'block');
                toggleVisibility('lnB29wbYkZgudKGQ9h9A', 'flex');
                toggleVisibility('form-text-Subtitle', 'block');
                video_render = "giọng đọc";
                resizer_subtittle_video();

                break;

            case '3':
                toggleVisibility('form-Reup', 'none');
                toggleVisibility('form-Subtitle', 'none');
                toggleVisibility('form-language', 'block');
                toggleVisibility('videoPosition', 'none');
                toggleVisibility('lnB29wbYkZgudKGQ9h9A', 'none');
                toggleVisibility('form-text-Subtitle', 'none');
                video_render = "None";
                break;
            case '4':
                toggleVisibility('form-Reup', 'none');
                toggleVisibility('form-Subtitle', 'block');
                toggleVisibility('form-language', 'none');
                toggleVisibility('videoPosition', 'block');
                toggleVisibility('lnB29wbYkZgudKGQ9h9A', 'flex');
                toggleVisibility('form-text-Subtitle', 'block');
                video_render = "giọng đọc";
                resizer_subtittle_video()
                break;
            case '5':
                toggleVisibility('form-Reup', 'none');
                toggleVisibility('form-Subtitle', 'none');
                toggleVisibility('form-language', 'none');
                toggleVisibility('videoPosition', 'none');
                toggleVisibility('lnB29wbYkZgudKGQ9h9A', 'none');
                toggleVisibility('form-text-Subtitle', 'none');
                break;
            default:
                toggleVisibility('form-Reup', 'none');
                toggleVisibility('form-Subtitle', 'none');
                toggleVisibility('form-language', 'none');
                toggleVisibility('videoPosition', 'none');
                toggleVisibility('lnB29wbYkZgudKGQ9h9A', 'none');
                toggleVisibility('form-text-Subtitle', 'none');
                video_render = "None";
                break;
        }

    });

    var modal = new bootstrap.Modal(document.getElementById('Modal-setting-language'));

    document.getElementById('btn-setting-language').addEventListener('click', function () {
        modal.show();
    });

    document.getElementById('modal-close').addEventListener('click', function () {
        modal.hide();
    });

    document.getElementById('modal-close-footer').addEventListener('click', function () {
        modal.hide();
    });

    setting_draw('restrictElement');

    function setting_draw(id) {
        const restrictElement = document.getElementById(id);

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
                        let x = parseFloat(target.style.left) || 0;
                        let y = parseFloat(target.style.top) || 0;

                        target.style.left = `${x + event.dx}px`;
                        target.style.top = `${y + event.dy}px`;

                        if (video_render.includes("giọng đọc")) {
                            Change_subtitle_size(target, 'lnB29wbYkZgudKGQ9h9A');
                        }
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
                    }),
                ],
                listeners: {
                    move: function (event) {
                        let target = event.target;
                        let x = parseFloat(target.style.left) || 0;
                        let y = parseFloat(target.style.top) || 0;

                        let newWidth = parseFloat(event.rect.width);
                        let newHeight = parseFloat(event.rect.height);

                        target.style.width = `${newWidth}px`;
                        target.style.height = `${newHeight}px`;

                        target.style.left = `${x + event.deltaRect.left}px`;
                        target.style.top = `${y + event.deltaRect.top}px`;

                        if (video_render.includes("giọng đọc")) {
                            Change_subtitle_size(target, 'lnB29wbYkZgudKGQ9h9A');
                        }
                    }
                }
            });
    }

    function Change_subtitle_size(target, id) {
        const targetElement = document.getElementById(id);
        targetElement.style.flexDirection = 'column';
        targetElement.style.lineHeight = 'normal';
        targetElement.style.overflowWrap = 'anywhere';
        targetElement.style.display = 'flex';
        targetElement.style.justifyContent = 'top';
        targetElement.style.textAlign = 'end';
        targetElement.style.letterSpacing = '0px';
        targetElement.style.top = target.style.top;
        targetElement.style.left = target.style.left;
        targetElement.style.width = target.style.width;
        targetElement.style.height = target.style.height;
        targetElement.style.zIndex = 'auto';
        targetElement.style.position = 'absolute';
        targetElement.style.fontSize = '30px';
        targetElement.style.fontFamily = 'Arial';
        targetElement.style.overflow = 'hidden';
        targetElement.style.textDecoration = 'underline';
        targetElement.style.fontWeight = 'bold';
        targetElement.style.fontStyle = 'italic';
        targetElement.style.color = 'red';
    }

});