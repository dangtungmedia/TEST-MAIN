document.addEventListener('DOMContentLoaded', function () {
    function getCSRFToken() {
        const csrfElement = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfElement ? csrfElement.value : null;
    }

    const host = window.location.host;
    const protocol = window.location.protocol;


    document.getElementById('success-outlined').addEventListener('change', function () {
        if (this.checked) {
            GetFolderSelected(true);

        }
    });

    document.getElementById('danger-outlined').addEventListener('change', function () {
        if (this.checked) {
            GetFolderSelected(false);
        }
    });


    //Lấy Thông Tin Folder Được Chọn
    function GetFolderSelected(is_content) {
        var userElement = document.getElementById('user-id');
        var userId = userElement.getAttribute('data-id');

        const protocol = window.location.protocol;
        const host = window.location.host;
        const url = `${protocol}//${host}/home/folders/get-folders/`;

        const dataToSend = {
            is_content: is_content,
            userId: userId,
        };

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
                console.log(data);
                let folderElement = document.getElementById('folder_name');
                folderElement.innerHTML = '';

                let channel_name = document.getElementById('channel_name');
                channel_name.innerHTML = '';
                data.folders.forEach(folder => {
                    let option = document.createElement('option');
                    option.value = folder.id;
                    option.text = folder.folder_name; // Assuming 'folder_name' is the field name
                    folderElement.appendChild(option);
                });
                GetProfileSelected()
            })
            .catch(error => {
                console.error('Error:', error);
            });

    }

    function GetProfileSelected() {
        folderId = document.getElementById('folder_name').value;
        if (folderId === '') {
            return;
        }
        console.log(folderId);
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
                let folderElement = document.getElementById('channel_name');
                folderElement.innerHTML = '';
                data.forEach(profile => {
                    let option = document.createElement('option');
                    option.value = profile.id;
                    option.text = profile.channel_name; // Assuming 'channel_name' is the field name
                    folderElement.appendChild(option);
                });

            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }

});
