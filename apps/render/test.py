import asyncio
        import edge_tts
        # Tạo từ điển ánh xạ mã ngôn ngữ và tên quốc gia
        language_to_country = {
            'af': 'South Africa',
            'sq': 'Albania',
            'am': 'Ethiopia',
            'ar': 'Saudi Arabia',
            'az': 'Azerbaijan',
            'bn': 'Bangladesh',
            'bs': 'Bosnia and Herzegovina',
            'bg': 'Bulgaria',
            'my': 'Myanmar',
            'ca': 'Catalonia',
            'zh': 'China',
            'hr': 'Croatia',
            'cs': 'Czech Republic',
            'da': 'Denmark',
            'nl': 'Netherlands',
            'en': 'United States',
            'et': 'Estonia',
            'fil': 'Philippines',
            'fi': 'Finland',
            'fr': 'France',
            'gl': 'Galicia',
            'ka': 'Georgia',
            'de': 'Germany',
            'el': 'Greece',
            'gu': 'India',
            'he': 'Israel',
            'hi': 'India',
            'hu': 'Hungary',
            'is': 'Iceland',
            'id': 'Indonesia',
            'ga': 'Ireland',
            'it': 'Italy',
            'ja': 'Japan',
            'jv': 'Indonesia',
            'kn': 'India',
            'kk': 'Kazakhstan',
            'km': 'Cambodia',
            'ko': 'Korea',
            'lo': 'Laos',
            'lv': 'Latvia',
            'lt': 'Lithuania',
            'mk': 'North Macedonia',
            'ms': 'Malaysia',
            'ml': 'India',
            'mt': 'Malta',
            'mr': 'India',
            'mn': 'Mongolia',
            'ne': 'Nepal',
            'nb': 'Norway',
            'ps': 'Afghanistan',
            'fa': 'Iran',
            'pl': 'Poland',
            'pt': 'Portugal',
            'ro': 'Romania',
            'ru': 'Russia',
            'sr': 'Serbia',
            'si': 'Sri Lanka',
            'sk': 'Slovakia',
            'sl': 'Slovenia',
            'so': 'Somalia',
            'es': 'Spain',
            'su': 'Indonesia',
            'sw': 'Swahili',
            'sv': 'Sweden',
            'ta': 'India',
            'te': 'India',
            'th': 'Thailand',
            'tr': 'Turkey',
            'uk': 'Ukraine',
            'ur': 'Pakistan',
            'uz': 'Uzbekistan',
            'vi': 'Vietnam',
            'cy': 'Wales',
            'zu': 'South Africa'
        }

        async def list_voices():
            voices_manager = await edge_tts.VoicesManager.create()
            voices = voices_manager.voices
            return voices

        # Chạy hàm để liệt kê các giọng đọc
        voices = asyncio.run(list_voices())


        # Tạo một danh sách để lưu các giọng đọc theo quốc gia
        # for voice in voices:
        #     language = voice['Locale'].split('-')[0]
        #     country = language_to_country.get(language, 'Unknown')
        #     name = f"{country}-{voice['Gender']}-{voice['ShortName']}"
        #     syle_voice.objects.create(
        #         voice_language = Voice_language.objects.get(id=1),
        #         name_voice =  name,
        #         style_name = voice['ShortName'],
        #     )
        # print("đã thêm xong giọng đọc")



function fetchProfileChannels(folderId) {
        const csrfToken = getCSRFToken();

        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        const url = `${protocol}//${host}/api/profilechannels/by-folder/${folderId}/`;
        console.log(`Fetching data from: ${url}`);

        fetch(url, {
            method: 'PATCH',
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
                const select = document.getElementById('profile_channel');
                select.innerHTML = ''; // Xóa các tùy chọn hiện có
                data.forEach(channel => {
                    const option = document.createElement('option');
                    option.value = channel.id;
                    option.textContent = "xxxxxxx"; // Đảm bảo rằng đây là tên trường chính xác
                    select.appendChild(option);
                });
            })
            .catch(error => {
                console.error('There was a problem with your fetch operation:', error);
            });
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
                    console.log(data)
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

        const url = `${protocol}//${host}/home/profiles/${profile_id}/`;
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
                console.log(JSON.stringify(data));

                select_choice('channel_font_text', data.channel_font_text);
                select_choice('channel_font_text_setting', data.channel_font_text);
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
            })
            .catch(error => {
                console.error('There was a problem with your fetch operation:', error);
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


    function add_slect_option(Id_slecect, channel, name) {
        const select = document.getElementById(Id_slecect);
        const option = document.createElement('option');
        option.value = channel.id;
        option.textContent = name; // Sử dụng đúng tên trường
        select.appendChild(option);
        select.value = channel.id;
    }

    function update_select_option(Id_select, channel, name) {
        const select = document.getElementById(Id_select);
        let option = select.querySelector(`option[value="${channel.id}"]`);
        option.textContent = name;
    }

    function delete_select_option(Id_select, folder_id) {
        const select = document.getElementById(Id_select);
        const option = select.querySelector(`option[value="${folder_id}"]`);
        if (option) {
            option.remove();
        } else {
            console.error(`Option with value "${folder_id}" not found in select "${Id_select}"`);
        }
    }



    $('#folder_name').change(function () {
        const folderId = $(this).val();
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
                console.log('Data received:', data);
                // Gọi hàm fetchProfileChannels để xử lý dữ liệu nhận được
                fetchProfileChannels(data, 'channel_name');
                fetchProfileChannels(data, 'channel_forder_name_setting');
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    });

    function fetchProfileChannels(data, name_id) {
        console.log('Fetched profile channels:', data);
        const select = document.getElementById(name_id);
        select.innerHTML = ''; // Xóa các tùy chọn hiện có

        data.forEach(channel => {
            const option = document.createElement('option');
            option.value = channel.id;
            option.textContent = channel.channel_name; // Đảm bảo rằng đây là tên trường chính xác
            select.appendChild(option);
        });
    }

    GetInforProfile();

    $('#folder-add').click(function () {
        console.log('Folder changed');
        const csrfToken = getCSRFToken();
        const folder_name = $('#input_folder_name').val();
        var userElement = document.getElementById('user-id');
        var userId = userElement.getAttribute('data-id');
        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        if (!folder_name) {
            console.error('Folder name not found');
            return;
        }

        const dataToSend = {
            folder_name: folder_name,
            use: userId
        };

        console.log('Data to send:', dataToSend);

        const url = `${protocol}//${host}/home/folders/`;
        console.log(`Fetching data from: ${url}`);

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dataToSend)
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', Array.isArray(data));
                console.log('Success:', Array.isArray(data));
                
                add_slect_option('folder_name', data, data.folder_name)
                add_slect_option('forder_setting', data, data.folder_name)

                // Tạo phần tử thông báo thành công
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Cập Thêm Thành Công Thư Mục ${data.folder_name}`;
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

            })

            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Có lỗi xảy ra khi thêm thư mục ${error.message}`;
                $('.btn-close').click();

                // Thêm phần tử thông báo vào đầu phần tử card-body
                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });
    });



    $('#folder-update').click(function () {
        console.log('Folder changed');
        const csrfToken = getCSRFToken();
        const folder_name = $('#input_folder_name').val();
        var userElement = document.getElementById('user-id');
        var userId = userElement.getAttribute('data-id');
        var folder_id = $('#folder_name').val();
        const protocol = window.location.protocol;
        const host = window.location.host;

        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        if (!folder_name) {
            console.error('Folder name not found');
            return;
        }

        const dataToSend = {
            id: folder_id,
            folder_name: folder_name,
            use: userId
        };

        console.log('Data to send:', dataToSend);

        const url = `${protocol}//${host}/home/folders/${folder_id}/`;
        console.log(`Fetching data from: ${url}`);

        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dataToSend)
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json();
            })
            .then(data => {

                update_select_option('folder_name', data, data.folder_name)
                update_select_option('forder_setting', data, data.folder_name)

                // Tạo phần tử thông báo thành công
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Cập Nhập Thành Công Thư Mục "${data.folder_name}"`;
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

            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Cập Nhập Thất bại ${error.message}`;
                $('.btn-close').click();

                // Thêm phần tử thông báo vào đầu phần tử card-body
                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });
    });

    $('#folder-delete').click(function () {
        console.log('delete changed');
        const csrfToken = getCSRFToken();
        const folder_name = $('#input_folder_name').val();
        var userElement = document.getElementById('user-id');
        var userId = userElement.getAttribute('data-id');
        var folder_id = $('#folder_name').val();
        const protocol = window.location.protocol;
        const host = window.location.host;

        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        if (!folder_name) {
            console.error('Folder name not found');
            return;
        }

        const url = `${protocol}//${host}/home/folders/${folder_id}/`;
        console.log(`Fetching data from: ${url}`);

        fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                if (response.status === 204) {
                    return { msg: `Xóa thành Công Thư Mục "${folder_name}"`, folder_name }; // Trả về đối tượng giả lập khi không có nội dung
                }
                return response.text().then(text => {
                    return text ? JSON.parse(text) : {}; // Phân tích JSON nếu có nội dung, nếu không trả về đối tượng trống
                });
            })
            .then(data => {
                console.log('Delete Success:', data);

                delete_select_option('folder_name', folder_id);
                delete_select_option('forder_setting', folder_id);

                // Tạo phần tử thông báo thành công
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success text-danger';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Xóa thành Công Thư Mục "${folder_name}"`;
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

            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger text-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Xóa Thư Mục Thất Bại: ${error.message}`;
                $('.btn-close').click();

                // Thêm phần tử thông báo vào đầu phần tử card-body
                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });
    });

    $('#add-channel').click(function () {
        const csrfToken = getCSRFToken();
        const channel_name = $('#input_profile_name').val();


        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        if (!channel_name) {
            console.error('Channel name not found');
            return;
        }

        const dataToSend = {
            channel_name: channel_name,
            folder_name: $('#folder_name').val(),
        };

        console.log('Data to send:', dataToSend);

        const url = `${protocol}//${host}/home/profiles/`;

        fetch(url, {

            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dataToSend)
        })

            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json();
            }
            )

            .then(data => {
                add_slect_option('channel_name', data, data.channel_name)
                add_slect_option('channel_forder_name_setting', data, data.channel_name)

                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Thêm Thành Công Profile "${data.channel_name}"`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(successAlert, cardBody.firstChild);
                    successAlert.style.display = 'block';
                    setTimeout(function () {
                        successAlert.style.display = 'none';
                    }, 5000);
                }

            }

            )
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Có lỗi xảy ra khi thêm Profile ${error.message}`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });


    });

    $('#update-channel').click(function () {
        const csrfToken = getCSRFToken();
        const channel_id = $('#channel_name').val();
        const channel_name = $('#input_profile_name').val();
        console.log(channel_id)

        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }


        const dataToSend = {
            id: channel_id,
            channel_name: channel_name,
        };
        console.log('Data to send:', dataToSend);

        const url = `${protocol}//${host}/home/profiles/${channel_id}/`;

        fetch(url, {

            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dataToSend)
        })

            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json();
            }
            )

            .then(data => {
                console.log(data)

                update_select_option('channel_name', data, data.channel_name)
                update_select_option('channel_forder_name_setting', data, data.channel_name)

                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Cập Nhập Thành Công  "${data.channel_name}"`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(successAlert, cardBody.firstChild);
                    successAlert.style.display = 'block';
                    setTimeout(function () {
                        successAlert.style.display = 'none';
                    }, 5000);
                }

            }
            )
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Cập Nhập Thất Bại ${error.message}`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });
    });


    $('#delete-channel').click(function () {
        const csrfToken = getCSRFToken();
        const channel_id = $('#channel_name').val();
        const channel_name = $('#input_profile_name').val();
        console.log(channel_id);

        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        const url = `${protocol}//${host}/home/profiles/${channel_id}/`;

        fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json().catch(() => ({}));  // Handle cases where the response is empty
            })
            .then(data => {
                console.log(data);
                delete_select_option('channel_name', channel_id);
                delete_select_option('channel_forder_name_setting', channel_id);

                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success text-danger';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Xóa thành công profile "${channel_name}"`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(successAlert, cardBody.firstChild);
                    successAlert.style.display = 'block';
                    setTimeout(function () {
                        successAlert.style.display = 'none';
                    }, 5000);
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Có lỗi xảy ra dổi thông tin Profile ${error.message}`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });
    });

    $('#channel_name').change(function () {
        GetInforProfile();
    });


    $('#save-fontext').click(function () {
        const dataToSend = {
            csrfToken: getCSRFToken(),
            channel_id: $('#channel_name').val(),
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
        const url = `${protocol}//${host}/home/profiles/${$('#channel_name').val()}/`;
        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(dataToSend)
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Cập Nhật Thông Tin Thành Công "${data.channel_name}"`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(successAlert, cardBody.firstChild);
                    successAlert.style.display = 'block';
                    setTimeout(function () {
                        successAlert.style.display = 'none';
                    }, 5000);
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Cập Nhật Thông Tin Thất Bại ${error.message}`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });

    });

    $('#save-voice').click(function () {
        const dataToSend = {
            csrfToken: getCSRFToken(),
            channel_id: $('#channel_name').val(),
            channel_voice_setting: $('#channel_voice_setting').val(),
            channel_voice_style: $('#channel_voice_style').val(),
            channel_voice_speed: $('#channel_voice_speed').val(),
            channel_voice_pitch: $('#channel_voice_pitch').val(),
            channel_voice_volume: $('#channel_voice_volume').val(),
            channel_text_voice: $('#channel_text_voice').val(),
        }
        const url = `${protocol}//${host}/home/profiles/${$('#channel_name').val()}/`;
        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(dataToSend)
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Cập Nhật Thông Tin Thành Công "${data.channel_name}"`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(successAlert, cardBody.firstChild);
                    successAlert.style.display = 'block';
                    setTimeout(function () {
                        successAlert.style.display = 'none';
                    }, 5000);
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Cập Nhật Thông Tin Thất Bại ${error.message}`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });
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


    $('#channel_voice,#channel_voice_setting').change(function () {
        $('#channel_voice, #channel_voice_setting').val($(this).val());
        GettylerVoice();
    });

    var initialText = $('#folder_name option:selected').text();
    $('#input_folder_name').val(initialText);

    $('#folder_name, #folder_setting').change(function () {
        var selectedText = $(this).find('option:selected').text();
        $('#folder_name, #forder_setting').val($(this).val());
        $('#input_folder_name').val(selectedText);
    });

    var initialText = $('#channel_name option:selected').text();
    $('#input_profile_name').val(initialText);

    $('#channel_name, #channel_forder_name_setting').change(function () {
        var selectedText = $(this).find('option:selected').text();
        $('#channel_name, #channel_forder_name_setting').val($(this).val());
        $('#input_profile_name').val(selectedText);
    });

    $('#save-profile').click(function () {
        const csrfToken = getCSRFToken();
        const channel_id = $('#channel_name').val();
        const channel_name = $('#input_profile_name').val();
        console.log(channel_id);

        if (!csrfToken) {
            console.error('CSRF token not found');
            return;
        }

        const dataToSend = {
            "channel_intro_active": false,
            "channel_intro_url": "",
            "channel_outro_active": false,
            "channel_outro_url": "",
            "channel_logo_active": false,
            "channel_logo_url": "",
            "channel_logo_position": "left",
            "channel_font_size": $('#channel_font_size').val(),
            "channel_font_bold": false,
            "channel_font_italic": false,
            "channel_font_underline": false,
            "channel_font_strikeout": false,
            "channel_font_color": $('#channel_font_color').val(),
            "channel_font_color_opacity": $('#channel_font_color_opacity').val(),
            "channel_font_color_troke": $('#channel_font_color_troke').val(),
            "channel_font_color_troke_opacity": $('#channel_font_color_troke_opacity').val(),
            "channel_stroke_text": $('#channel_stroke_text').val(),
            "channel_font_background": $('#channel_font_background').val(),
            "channel_font_background_opacity": $('#channel_font_background_opacity').val(),
            "channel_font_subtitle": $('#channel_font_subtitle').val(),
            "channel_text_voice": $('#channel_text_voice').val(),
            "channel_title": $('#channel_title').val(),
            "channel_description": $('#channel_description').val(),
            "channel_keywords": $('#channel_keywords').val(),
            "channel_time_upload": $('#channel_time_upload').val(),
            "channel_url": $('#channel_url').val(),
            "channel_email_login": $('#channel_email_login').val(),
            "channel_vps_upload": $('#channel_vps_upload').val(),
            "folder_name": $('#folder_name').val(),
            "channel_font_text": $('#channel_font_text').val(),
            "channel_voice": $('#channel_voice').val(),
            "channel_voice_style": $('#channel_voice_style').val()
        };
        console.log('Data to send:', dataToSend);

        const url = `${protocol}//${host}/home/profiles/${channel_id}/`;

        fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(dataToSend)
        })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.detail || 'Network response was not ok ' + response.statusText); });
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                const successAlert = document.createElement('div');
                successAlert.className = 'alert alert-success';
                successAlert.role = 'alert';
                successAlert.id = 'success-alert';
                successAlert.innerText = data.msg || `Cập Nhật Thông Tin Thành Công "${data.channel_name}"`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(successAlert, cardBody.firstChild);
                    successAlert.style.display = 'block';
                    setTimeout(function () {
                        successAlert.style.display = 'none';
                    }, 5000);
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                const dangerAlert = document.createElement('div');
                dangerAlert.className = 'alert alert-danger';
                dangerAlert.role = 'alert';
                dangerAlert.id = 'danger-alert';
                dangerAlert.innerText = error.message || `Cập Nhật Thông Tin Thất Bại ${error.message}`;
                $('.btn-close').click();

                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(dangerAlert, cardBody.firstChild);
                    dangerAlert.style.display = 'block';
                    setTimeout(function () {
                        dangerAlert.style.display = 'none';
                    }, 5000);
                }
            });
    });
