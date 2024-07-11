$(document).ready(function () {
    // Khi một radio button thay đổi
    $('input[type="radio"]').change(function () {
        // Kiểm tra radio button nào được chọn
        if ($('#id_logo_position_0').is(':checked')) {
            // Di chuyển logo sang trái
            $('.logo').css('right', '').css('left', '10px');
        } else if ($('#id_logo_position_1').is(':checked')) {
            // Di chuyển logo sang phải
            $('.logo').css('left', '').css('right', '10px');
        }
    });
});

// Thêm sự kiện 'input' để cập nhật nội dung khi văn bản trong textarea thay đổi
document.getElementById('form-text-Subtitle').addEventListener('input', function () {
    // Cập nhật nội dung của phần tử Subtitle với nội dung mới từ textarea
    document.getElementById('text-Subtitle').textContent = this.value;
});

document.getElementById('font-Subtitle').addEventListener('change', function () {
    // Cập nhật font của phần tử Subtitle
    document.getElementById('Subtitle').style.fontFamily = this.value;

});

document.getElementById('size-Subtitle').addEventListener('change', function () {
    // Cập nhật kích thước font của phần tử Subtitle
    document.getElementById('Subtitle').style.fontSize = this.value + 'px';
});

document.getElementById('font-bold').addEventListener('change', function () {
    // Cập nhật font-weight của phần tử Subtitle
    document.getElementById('Subtitle').style.fontWeight = this.checked ? 'bold' : 'normal';
});

document.getElementById('font-Italic').addEventListener('change', function () {
    // Cập nhật font-style của phần tử Subtitle
    document.getElementById('Subtitle').style.fontStyle = this.checked ? 'italic' : 'normal';
});

document.getElementById('font-Underline').addEventListener('change', function () {
    // Cập nhật text-decoration của phần tử Subtitle
    document.getElementById('Subtitle').style.textDecoration = this.checked ? 'underline' : 'none';
});

document.getElementById('font-Strikeout').addEventListener('change', function () {
    // Cập nhật text-decoration của phần tử Subtitle
    document.getElementById('Subtitle').style.textDecoration = this.checked ? 'line-through' : 'none';
});


document.getElementById('color-text').addEventListener('change', updateColor);
document.getElementById('opacity-color-text').addEventListener('input', updateColor);

function updateColor() {
    let color = document.getElementById('color-text').value;
    let opacity = document.getElementById('opacity-color-text').value / 100;
    let rgbaColor = `rgba(${parseInt(color.substr(1, 2), 16)}, ${parseInt(color.substr(3, 2), 16)}, ${parseInt(color.substr(5, 2), 16)}, ${opacity})`;
    document.getElementById('Subtitle').style.color = rgbaColor;
}


document.getElementById('color-text-border').addEventListener('change', updateBorderColor);
document.getElementById('opacity-color-text-border').addEventListener('input', updateBorderColor);

function updateBorderColor() {
    let color = document.getElementById('color-text-border').value;
    let opacity = document.getElementById('opacity-color-text-border').value / 100;
    let rgbaColor = `rgba(${parseInt(color.substr(1, 2), 16)}, ${parseInt(color.substr(3, 2), 16)}, ${parseInt(color.substr(5, 2), 16)}, ${opacity})`;
    document.getElementById('text-Subtitle').style.textShadow = `0 0 0 ${rgbaColor}`;

    const r = document.getElementById('size-color-text-border').value; // width of outline in pixels
    const n = Math.ceil(2 * Math.PI * r); // number of shadows
    var str = '';
    for (var i = 0; i < n; i++) { // append shadows in n evenly distributed directions
        const theta = 2 * Math.PI * i / n;
        str += `${r * Math.cos(theta)}px ${r * Math.sin(theta)}px 0 ${rgbaColor}${i == n - 1 ? '' : ','}`;
    }
    document.getElementById("text-Subtitle").style.textShadow = str;
}

document.getElementById('size-color-text-border').addEventListener('change', function () {
    // Cập nhật text-decoration của phần tử Subtitle
    updateBorderColor()
});


document.getElementById('background-color').addEventListener('change', updateBackgroundColor);
document.getElementById('opacity-background-color-text').addEventListener('input', updateBackgroundColor);

function updateBackgroundColor() {
    let color = document.getElementById('background-color').value;
    let opacity = document.getElementById('opacity-background-color-text').value / 100;
    let rgbaColor = `rgba(${parseInt(color.substr(1, 2), 16)}, ${parseInt(color.substr(3, 2), 16)}, ${parseInt(color.substr(5, 2), 16)}, ${opacity})`;
    document.getElementById('Subtitle').style.backgroundColor = rgbaColor;
}