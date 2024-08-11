document.addEventListener('DOMContentLoaded', function () {
    function getCSRFToken() {
        const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfElement ? csrfElement.value : null;
    }


    const host = window.location.host;
    const protocol = window.location.protocol;

    const successOutlined = document.getElementById('success-outlined');


    const dangerOutlined = document.getElementById('danger-outlined');

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

    function select_choice(Id_slecect, value) {
        const selectElement = document.getElementById(Id_slecect);
        // Check if selectElement is found
        if (!selectElement) {
            return;
        }
        const options = selectElement.options;
        let found = false;

        for (let i = 0; i < options.length; i++) {
            if (options[i].value == value) { // Use == for type coercion comparison
                selectElement.selectedIndex = i;
                found = true;
                break;
            }
        }

        // If the desired value is not found, select the first option
        if (!found) {
            selectElement.selectedIndex = 0;
        }
    }

    function GettylerVoice() {
        const csrfToken = getCSRFToken();

        console.log('Get Voice');
        id_voice_profile = $('#channel_voice').val();


        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        const url = `${protocol}//${host}/home/styler-voice/by-Voide/${id_voice_profile}/`;

        console.log(`Fetching data from: ${url}`);

        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                console.log(`Received data: ${JSON.stringify(data)}`); // Log dữ liệu nhận được
                if (!Array.isArray(data)) {
                    throw new TypeError('Expected an array but did not receive one');
                }
                const select = document.getElementById('channel_voice_style');
                select.innerHTML = ''; // Xóa các tùy chọn hiện có
                data.forEach(channel => {
                    const option = document.createElement('option');
                    option.value = channel.id;
                    option.text = channel.name_voice; // Đảm bảo rằng đây là tên trường chính xác
                    select.appendChild(option);
                });
            })
            .catch(error => {
                console.error('There was a problem with your fetch operation:', error);
            });
    }

    // Lấy Thông Tin Folder Được Chọn
    function GetFolderSelected(is_content) {
        const userElement = document.getElementById('user-id');
        if (!userElement) {
            console.error('User element not found');
            return;
        }
        const userId = userElement.getAttribute('data-id');

        const url = `${protocol}//${host}/home/folders/get-folders/`;

        const dataToSend = {
            is_content: is_content,
            userId: userId,
        };

        const folderElement = document.getElementById('folder_name');
        const folderSetting = document.getElementById('folder_setting');


        if (!folderElement) {
            console.error('Folder name element not found');
            return;
        }
        if (!folderSetting) {
            console.error('Folder setting element not found');
            return;
        }

        folderElement.innerHTML = '';
        folderSetting.innerHTML = '';

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

                    let option2 = document.createElement('option');
                    option2.value = folder.id;
                    option2.text = folder.folder_name; // Assuming 'folder_name' is the field name

                    folderSetting.appendChild(option2);
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
        const channelNameSetting = document.getElementById('channel_folder_name_setting');
        channelElement.innerHTML = '';
        channelNameSetting.innerHTML = '';

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
                if (!channelNameSetting) {
                    console.error('Channel folder name setting element not found');
                    return;
                }
                data.forEach(profile => {
                    console.log(profile);

                    // Tạo tùy chọn cho channelElement
                    let option = document.createElement('option');
                    option.value = profile.id;
                    option.text = profile.channel_name; // Assuming 'channel_name' is the field name
                    channelElement.appendChild(option);

                    // Tạo tùy chọn cho channelNameSetting
                    let option2 = document.createElement('option');
                    option2.value = profile.id;
                    option2.text = profile.channel_name; // Assuming 'channel_name' is the field name
                    channelNameSetting.appendChild(option2);
                });
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }


    // Thêm Tùy Chọn Vào Select
    function add_slect_option(Id_slecect, channel, name) {
        const select = document.getElementById(Id_slecect);
        const option = document.createElement('option');
        option.value = channel.id;
        option.textContent = name; // Sử dụng đúng tên trường
        select.appendChild(option);
        select.value = channel.id;
    }

    // Cập Nhập Tùy Chọn
    function update_select_option(Id_select, channel, name) {
        const select = document.getElementById(Id_select);
        let option = select.querySelector(`option[value="${channel.id}"]`);
        option.textContent = name;
    }

    // Xóa Tùy Chọn
    function delete_select_option(Id_select, folder_id) {
        const select = document.getElementById(Id_select);
        const option = select.querySelector(`option[value="${folder_id}"]`);
        if (option) {
            option.remove();
        } else {
            console.error(`Option with value "${folder_id}" not found in select "${Id_select}"`);
        }
    }


    function GetIsContent() {
        const successOutlined = document.getElementById('success-outlined');
        const dangerOutlined = document.getElementById('danger-outlined');
        if (successOutlined.checked) {
            return true;
        } else if (dangerOutlined.checked) {
            return false;
        }
    }

    $('#folder-add').click(async function () {
        var is_content = GetIsContent();
        var userElement = document.getElementById('user-id');
        var userId = userElement.getAttribute('data-id');
        const url = `${protocol}//${host}/home/folders/`;
        const method = 'POST';

        const dataToSend = {
            is_content: is_content,
            use: userId,
            folder_name: $('#input_folder_name').val(),
        };

        const text = 'Thêm Thành Công Thư Mục  "' + $('#input_folder_name').val() + ' "!';
        const text_error = 'Thêm Thư Mục Thất Bại  "' + $('#input_folder_name').val() + ' "!';

        try {
            const data = await UpdateData(url, method, dataToSend, text, text_error);
            add_slect_option('folder_name', data, data.folder_name);
            add_slect_option('folder_setting', data, data.folder_name);

        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
        GetInforProfile();
    });

    $('#folder-update').click(async function () {
        var userElement = document.getElementById('user-id');
        var userId = userElement.getAttribute('data-id');
        const folder_id = $('#folder_name').val();
        const folder_name = $('#input_folder_name').val();
        const url = `${protocol}//${host}/home/folders/${folder_id}/`;
        const method = 'PATCH';

        const text = 'Cập Nhập Thành Công  Thư Mục "' + $('#input_folder_name').val() + ' "!';
        const text_error = 'Cập Nhập Thư Mục Thất Bại  "' + $('#input_folder_name').val() + ' "!';

        const dataToSend = {
            id: folder_id,
            folder_name: folder_name,
            use: userId
        };
        try {
            const data = await UpdateData(url, method, dataToSend, text, text_error);
            update_select_option('folder_name', data, data.folder_name)
            update_select_option('folder_setting', data, data.folder_name)

        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
        GetInforProfile();
    });


    $('#folder-delete').click(async function () {
        const folder_id = $('#folder_name').val();
        const folder_text = $('#folder_name option:selected').text();
        const url = `${protocol}//${host}/home/folders/${folder_id}/`;
        const method = 'DELETE';

        const text = 'Xóa Thành Công Thư Mục "' + folder_text + ' "!';
        const text_error = 'Xóa Thư Mục Thất Bại "' + $('#input_folder_name').val() + ' "!';

        try {
            await UpdateData(url, method, {}, text, text_error);
            delete_select_option('folder_name', folder_id);
            delete_select_option('folder_setting', folder_id);
        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
        GetInforProfile();
    });

    $('#profile-add').click(async function () {
        const folder_id = $('#folder_name').val();
        const url = `${protocol}//${host}/home/profiles/`;
        const method = 'POST';

        const dataToSend = {
            folder_name: folder_id,
            channel_name: $('#input_profile_name').val(),
        };

        const text = 'Thêm Thành Công Kênh "' + $('#input_profile_name').val() + ' "!';
        const text_error = 'Thêm Kênh Thất Bại "' + $('#input_profile_name').val() + ' "!';

        try {
            const data = await UpdateData(url, method, dataToSend, text, text_error);
            add_slect_option('channel_name', data, data.channel_name);
            add_slect_option('channel_folder_name_setting', data, data.channel_name);
        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
        GetInforProfile();
    });

    $('#profile-update').click(async function () {
        const profile_id = $('#channel_name').val();
        const url = `${protocol}//${host}/home/profiles/${profile_id}/`;
        const method = 'PATCH';

        const dataToSend = {
            id: profile_id,
            channel_name: $('#input_profile_name').val(),
        };

        const text = 'Cập Nhập Thành Công Kênh "' + $('#input_profile_name').val() + ' "!';
        const text_error = 'Cập Nhập Kênh Thất Bại "' + $('#input_profile_name').val() + ' "!';

        try {
            const data = await UpdateData(url, method, dataToSend, text, text_error);
            update_select_option('channel_name', data, data.channel_name);
            update_select_option('channel_folder_name_setting', data, data.channel_name);
        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
        GetInforProfile();
    });

    $('#profile-delete').click(async function () {
        const profile_id = $('#channel_name').val();
        const url = `${protocol}//${host}/home/profiles/${profile_id}/`;
        const method = 'DELETE';

        const text = 'Xóa Thành Công Kênh "' + $('#input_profile_name').val() + ' "!';
        const text_error = 'Xóa Kênh Thất Bại "' + $('#input_profile_name').val() + ' "!';

        try {
            await UpdateData(url, method, {}, text, text_error);
            delete_select_option('channel_name', profile_id);
            delete_select_option('channel_folder_name_setting', profile_id);
        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
        GetInforProfile();
    });

    async function UpdateData(url, method, dataToSend, text, text_error) {
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(dataToSend)
            });

            if (!response.ok) {
                let errMessage = 'Network response was not ok ' + response.statusText;
                try {
                    const err = await response.json();
                    errMessage = err.detail || errMessage;
                } catch (jsonError) {
                    // Ignore JSON parsing error and use the default message
                }
                throw new Error(errMessage);
            }

            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                data = {}; // If response is empty, use an empty object
            }

            console.log('Success:', Array.isArray(data));

            // Tạo phần tử thông báo thành công
            const successAlert = document.createElement('div');
            successAlert.className = 'alert alert-success';
            successAlert.role = 'alert';
            successAlert.id = 'success-alert';
            successAlert.innerText = text;
            $('.btn-close').click();

            // Thêm phần tử thông báo vào đầu phần tử card-body
            const cardBody = document.querySelector('.card-body');
            if (cardBody) {
                cardBody.insertBefore(successAlert, cardBody.firstChild);
                successAlert.style.display = 'block';
                setTimeout(function () {
                    successAlert.style.display = 'none';
                }, 5000);
            }
            return data;
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);

            const dangerAlert = document.createElement('div');
            dangerAlert.className = 'alert alert-danger';
            dangerAlert.role = 'alert';
            dangerAlert.id = 'danger-alert';
            dangerAlert.innerText = text_error;
            $('.btn-close').click();

            // Thêm phần tử thông báo vào đầu phần tử card-body
            const cardBody = document.querySelector('.card-body');
            if (cardBody) {
                cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                dangerAlert.style.display = 'block';
                setTimeout(function () {
                    dangerAlert.style.display = 'none';
                }, 5000);
            } else {
                console.error('Card body element not found');
            }
            throw error; // Để lỗi này được xử lý ở phần gọi hàm

        }

    }

    $('#folder_name, #folder_setting').change(function () {
        var selectedText = $(this).find('option:selected').text();
        $('#folder_name, #folder_setting').val($(this).val());
        $('#input_folder_name').val(selectedText);
        GetProfileSelected();
    });

    $('#channel_name, #channel_folder_name_setting').change(function () {
        var selectedText = $(this).find('option:selected').text();
        $('#channel_name, #channel_folder_name_setting').val($(this).val());
        $('#input_profile_name').val(selectedText);
        GetInforProfile();
    });


    $('#channel_font_text, #channel_font_text_setting_2').change(function () {
        $('#channel_font_text, #channel_font_text_setting_2').val($(this).val());
    });

    function GetInforProfile() {
        const profile_id = document.getElementById('channel_name');
        if (!profile_id) {
            console.error('Profile element not found');
            return;
        }

        const csrfToken = getCSRFToken();
        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        const url = `${protocol}//${host}/home/profiles/${profile_id.value}/`;
        console.log(`Fetching data from: ${url}`);

        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                $('#channel_font_size').val(data.channel_font_size);

                $('#channel_font_color').val(data.channel_font_color);
                $('#channel_font_color_opacity').val(data.channel_font_color_opacity);


                $('#channel_font_color_troke').val(data.channel_font_color_troke);
                $('#channel_font_color_troke_opacity').val(data.channel_font_color_troke_opacity);

                $('#channel_font_background').val(data.channel_font_background);
                $('#channel_font_background_opacity').val(data.channel_font_background_opacity);

                $('#channel_stroke_text').val(data.channel_stroke_text);
                $('#channel_font_subtitle').val(data.channel_font_subtitle);

                select_choice('channel_voice', data.channel_voice);
                select_choice('channel_voice_setting', data.channel_voice);
                GettylerVoice();
                select_choice('channel_voice_style', data.channel_voice_style);

                $('#channel_title').val(data.channel_title);
                $('#channel_description').val(data.channel_description);
                $('#channel_keyword').val(data.channel_keyword);
                $('#channel_time_upload').val(data.channel_time_upload);
                $('#channel_url').val(data.channel_url);
                $('#channel_email_login').val(data.channel_email_login);
                $('#channel_vps_upload').val(data.channel_vps_upload);

                select_choice('channel_font_text', data.channel_font_text);
                select_choice('channel_font_text_setting_2', data.channel_font_text);

                console.log('Get Infor Profile');
                console.log('Get Infor Profile');
                show_Subtitle();

            })
            .catch(error => {
                console.error('There was a problem with your fetch operation:', error);
            });

    }

    $('#channel_voice,#channel_voice_setting').change(function () {
        $('#channel_voice, #channel_voice_setting').val($(this).val());
        GettylerVoice();
    });


    $('#save-fontext').click(async function () {
        const url = `${protocol}//${host}/home/profiles/${$('#channel_name').val()}/`;
        const method = 'PATCH';

        const dataToSend = {
            id: $('#channel_name').val(),
            channel_font_text: $('#channel_font_text').val(),
            channel_font_size: $('#channel_font_size').val(),
            channel_font_color: $('#channel_font_color').val(),
            channel_font_color_opacity: $('#channel_font_color_opacity').val(),
            channel_font_color_troke: $('#channel_font_color_troke').val(),
            channel_font_color_troke_opacity: $('#channel_font_color_troke_opacity').val(),
            channel_font_background: $('#channel_font_background').val(),
            channel_font_background_opacity: $('#channel_font_background_opacity').val(),
            channel_stroke_text: $('#channel_stroke_text').val(),
            channel_font_subtitle: $('#channel_font_subtitle').val(),
        }
        console.log(dataToSend);
        const text = 'Cập Nhập Thành Công Font Text!';
        const text_error = 'Cập Nhập Font Text Thất Bại!';

        try {
            await UpdateData(url, method, dataToSend, text, text_error);
        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
    });

    $('#save-voice').click(async function () {
        const url = `${protocol}//${host}/home/profiles/${$('#channel_name').val()}/`;
        const method = 'PATCH';
        const dataToSend = {
            id: $('#channel_name').val(),
            channel_voice: $('#channel_voice').val(),
            channel_voice_style: $('#channel_voice_style').val(),
        }
        console.log(dataToSend);
        const text = 'Cập Nhập Thành Công Voice!';
        const text_error = 'Cập Nhập Voice Thất Bại!';

        try {
            await UpdateData(url, method, dataToSend, text, text_error);
        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
    });

    $('#save-profile').click(async function () {
        const url = `${protocol}//${host}/home/profiles/${$('#channel_name').val()}/`;
        const method = 'PATCH';
        const dataToSend = {
            id: $('#channel_name').val(),
            channel_title: $('#channel_title').val(),
            channel_description: $('#channel_description').val(),
            channel_keyword: $('#channel_keyword').val(),
            channel_time_upload: $('#channel_time_upload').val(),
            channel_url: $('#channel_url').val(),
            channel_email_login: $('#channel_email_login').val(),
            channel_vps_upload: $('#channel_vps_upload').val(),
            channel_font_text: $('#channel_font_text').val(),
            channel_font_size: $('#channel_font_size').val(),
            channel_font_color: $('#channel_font_color').val(),
            channel_font_color_opacity: $('#channel_font_color_opacity').val(),
            channel_font_color_troke: $('#channel_font_color_troke').val(),
            channel_font_color_troke_opacity: $('#channel_font_color_troke_opacity').val(),
            channel_font_background: $('#channel_font_background').val(),
            channel_font_background_opacity: $('#channel_font_background_opacity').val(),
            channel_stroke_text: $('#channel_stroke_text').val(),
            channel_font_subtitle: $('#channel_font_subtitle').val(),
            channel_title: $('#channel_title').val(),
            channel_description: $('#channel_description').val(),
            channel_keyword: $('#channel_keyword').val(),
            channel_time_upload: $('#channel_time_upload').val(),
            channel_url: $('#channel_url').val(),
            channel_email_login: $('#channel_email_login').val(),
            channel_vps_upload: $('#channel_vps_upload').val(),
        }
        console.log(dataToSend);
        const text = 'Cập Nhập Thành Công Profile!';
        const text_error = 'Cập Nhập Profile Thất Bại!';

        try {
            await UpdateData(url, method, dataToSend, text, text_error);
        } catch (error) {
            console.error('Lỗi khi cập nhật dữ liệu:', error);
        }
    });

    $("#random-time").click(function () {
        $('#channel_time_upload').val('');
        $('#channel_time_upload').val(generateTimeSlots());
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

    function show_Subtitle() {
        $("#text-Subtitle").text($('#channel_subtitle_text').val());
        $("#text-Subtitle").css('font-size', $('#channel_font_size').val() + 'px');
        var selectedText = $("#channel_font_text_setting_2 option:selected").text();
        $("#text-Subtitle").css('font-family', selectedText);

        $("#text-Subtitle").css('font-weight', $('#channel_font_bold').is(':checked') ? 'bold' : 'normal');
        $("#text-Subtitle").css('font-style', $('#channel_font_italic').is(':checked') ? 'italic' : 'normal');
        $("#text-Subtitle").css('text-decoration', $('#channel_font_underline').is(':checked') ? 'underline' : 'none');
        $("#text-Subtitle").css('text-decoration', $('#channel_font_strikeout').is(':checked') ? 'line-through' : 'none');

        let color = document.getElementById('channel_font_color').value;
        let opacity = document.getElementById('channel_font_color_opacity').value / 100;
        let rgbaColor = `rgba(${parseInt(color.substr(1, 2), 16)}, ${parseInt(color.substr(3, 2), 16)}, ${parseInt(color.substr(5, 2), 16)}, ${opacity})`;
        document.getElementById('text-Subtitle').style.color = rgbaColor;

        let backgroundColor = document.getElementById('channel_font_background').value;
        let backgroundOpacity = document.getElementById('channel_font_background_opacity').value / 100;
        let rgbaBackgroundColor = `rgba(${parseInt(backgroundColor.substr(1, 2), 16)}, ${parseInt(backgroundColor.substr(3, 2), 16)}, ${parseInt(backgroundColor.substr(5, 2), 16)}, ${backgroundOpacity})`;
        document.getElementById('text-Subtitle').style.background = rgbaBackgroundColor;

        let strokeColor = document.getElementById('channel_font_color_troke').value;
        let strokeOpacity = document.getElementById('channel_font_color_troke_opacity').value / 100;
        let rgbaStrokeColor = `rgba(${parseInt(strokeColor.substr(1, 2), 16)}, ${parseInt(strokeColor.substr(3, 2), 16)}, ${parseInt(strokeColor.substr(5, 2), 16)}, ${strokeOpacity})`;
        document.getElementById('text-Subtitle').style.textShadow = `0 0 0 ${rgbaStrokeColor}`;

        const r = document.getElementById('channel_stroke_text').value; // width of outline in pixels
        const n = Math.ceil(2 * Math.PI * r); // number of shadows
        var str = '';
        for (var i = 0; i < n; i++) { // append shadows in n evenly distributed directions
            const theta = 2 * Math.PI * i / n;
            str += `${r * Math.cos(theta)}px ${r * Math.sin(theta)}px 0 ${rgbaStrokeColor}${i == n - 1 ? '' : ','}`;
        }
        document.getElementById("text-Subtitle").style.textShadow = str;
    }

    $(document).ready(function () {
        $('#channel_font_subtitle').on('input', function () {
            // Lấy giá trị hiện tại của textarea
            var subtitleText = $(this).val();
            // Cập nhật nội dung của span
            $('#text-Subtitle').text(subtitleText);
        });
    });

    $('#channel_font_text_setting_2').change(function () {
        show_Subtitle();
    });

    $('#channel_font_size').change(function () {
        show_Subtitle();
    });

    $('#channel_font_color').change(function () {
        show_Subtitle();
    });

    $('#channel_font_color').change(function () {
        show_Subtitle();
    });

    $('#channel_font_color_opacity').change(function () {
        show_Subtitle();
    });

    $('#channel_font_color_troke').change(function () {
        show_Subtitle();
    });

    $('#channel_font_color_troke_opacity').change(function () {
        show_Subtitle();
    });

    $('#channel_font_background').change(function () {
        show_Subtitle();
    });

    $('#channel_font_background_opacity').change(function () {
        show_Subtitle();
    });

    $('#channel_stroke_text').change(function () {
        show_Subtitle();
    });

    $('#channel_font_subtitle').change(function () {
        show_Subtitle();
    });
    GetInforProfile()
}); 
