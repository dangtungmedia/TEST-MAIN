$(document).ready(function(){
        show_infor_channel();
        $('#folder_name').change(function(){
            var folder_name = $(this).val();
            $.ajax({
                url: "{% url 'home:load-channel' %}",
                type: "GET",
                data: {
                    folder_name: folder_name
                },
                success: function(data){
                    $("#channel_name").empty();
                    if (data.length > 0){
                        $.each(data, function(index, value){
                            $("#channel_name").append('<option value="'+value.id+'">'+value.channel_name+'</option>');
                        });
                    } else {
                        $("#channel_name").append('<option value="">-----</option>');
                    }
                    show_infor_channel();
                }
            });
        });



        $('input[type="radio"]').change(function () {
            // Kiểm tra radio button nào được chọn
           if ($('#flexRadioDefault1').is(':checked')) {
               // Di chuyển logo sang trái
               $('.logo').css('right', '').css('left', '10px');
           } else if ($('#flexRadioDefault2').is(':checked')) {
               // Di chuyển logo sang phải
               $('.logo').css('left', '').css('right', '10px');
           }
       });

       $("#channel_font_text").change(function(){
           $('#channel_font_text_setting').val($('#channel_font_text').val());
       });

       $("#channel_font_text_setting").change(function(){
           $('#channel_font_text').val($('#channel_font_text_setting').val());
       });

       $("#button-open-intro").click(function() {
           $("#channel_intro_input_file").click();
       });
       handleInputChange("#channel_intro_input_file", "#button-open-intro", "#channel_intro_url");
       
       $("#button-open-outro").click(function() {
           $("#channel_outro_input_file").click();
       });
       handleInputChange("#channel_outro_input_file", "#button-open-outro", "#channel_outro_url");
       
       $("#button-open-logo").click(function() {
           $("#channel_logo_input_file").click();
       });
       handleInputChange("#channel_logo_input_file", "#button-open-logo", "#channel_logo_url");

       $("#channel_subtitle_text").change(function(){
           show_Subtitle()
       });
       $("#channel_font_size").change(function(){
           show_Subtitle()
       });

       $("#channel_font_text_setting").change(function(){
           show_Subtitle()
       });

       $("#channel_font_bold").change(function(){
           show_Subtitle()
       });

       $("#channel_font_italic").change(function(){
           show_Subtitle()
       });

       $("#channel_font_underline").change(function(){
           show_Subtitle()
       });

       $("#channel_font_strikeout").change(function(){
           show_Subtitle()
       });

       $("#channel_font_color").change(function(){
           show_Subtitle()
       });

       $("#channel_font_color_opacity").change(function(){
        show_Subtitle()
        });

        $("#channel_font_background").change(function(){
            show_Subtitle()
        });

        $("#channel_font_background_opacity").change(function(){
            show_Subtitle()
        });

        $("#channel_font_color_troke").change(function(){
            show_Subtitle()
        });

        $("#channel_font_color_troke_opacity").change(function(){
            show_Subtitle()
        });

        $("#channel_stroke_text").change(function(){
            show_Subtitle()
        });
    
        $("#random-time").click(function(){
            $('#channel_time_upload').val('');
            $('#channel_time_upload').val(generateTimeSlots());
        });
    

        $('#channel_name').change(function(){
            show_infor_channel();
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
        
        function show_infor_channel(){
            var channel_id = $("#channel_name").val();
            $.ajax({
                url: "{% url 'home:load-channel-infor' %}",
                type: "GET",
                data: {
                    channel_id: channel_id
                },
                success: function(data){
                    $('#channel_intro_active').prop('checked', data.channel_intro_active|| false);
                    $('#channel_intro_url').val(data.channel_intro_url||'');
                    $('#channel_outro_active').prop('checked',data.channel_outro_active||false);
                    $('#channel_outro_url').val(data.channel_outro_url||'');
                    $('#channel_logo_active').prop('checked',data.channel_logo_active||false);
                    $('#channel_logo_url').val(data.channel_logo_url||'');
                    $('#channel_font_text').val(data.channel_font_text||'');
                    $('#channel_voice').val(data.channel_voice||'');
                    $('#channel_title').val(data.channel_title||'');
                    $('#channel_description').val(data.channel_description||'');
                    $('#channel_keywords').val(data.channel_keywords||'');
                    $('#channel_time_upload').val(data.channel_time_upload||'');
                    $('#channel_url').val(data.channel_url||'');
                    $('#channel_email_login').val(data.channel_email_login||'');
                    $('#channel_vps_upload').val(data.channel_vps_upload||'');
                    $('#channel_font_text_setting').val(data.channel_font_text_setting||'');
                    $('#channel_font_size').val(data.channel_font_size||40);
                    $('#channel_font_bold').prop('checked', data.channel_font_bold||false);
                    $('#channel_font_italic').prop('checked', data.channel_font_italic||false);
                    $('#channel_font_underline').prop('checked', data.channel_font_underline||false);
                    $('#channel_font_strikeout').prop('checked', data.channel_font_strikeout||false);
                    $('#channel_font_color').val(data.channel_font_color||'#FFFFFF');
                    $('#channel_font_color_opacity').val(data.channel_font_color_opacity||100);
                    $('#channel_font_color_troke').val(data.channel_font_color_troke||' #000000');
                    $('#channel_font_color_troke_opacity').val(data.channel_font_color_troke_opacity||100);
                    $('#channel_font_background').val(data.channel_font_background||'#000000');
                    $('#channel_font_background_opacity').val(data.channel_font_background_opacity||0);
                    $('#channel_stroke_text').val(data.channel_stroke_text||1);
                    $('text-Subtitle').text(data.channel_subtitle_text||'Đây là phụ đề của video');
                    $('#channel_subtitle_text').val(data.channel_subtitle_text||'Đây là phụ đề của video');

                    if(data.channel_logo_position == 'left'){
                        $('#flexRadioDefault1').prop('checked', true);
                        $('#flexRadioDefault1').click();
                    } else {
                        $('#flexRadioDefault2').prop('checked', true);
                        $('#flexRadioDefault2').click();
                    }
                    show_intro_video();
                    show_Subtitle();
                }
            });
        }


        function handleInputChange(inputId, buttonId, urlId) {
            $(inputId).change(function() {
                // Kiểm tra xem có tệp nào được chọn không
                if (this.files && this.files.length > 0) {
                    // Có tệp được chọn, thực hiện các hành động bạn muốn thực hiện
                    $(buttonId).hide();
                    $(urlId).hide();
                    $(inputId).show();
                } else {
                    // Không có tệp nào được chọn
                    show_input(); // Nếu show_input() là hàm chung, bạn có thể gọi nó ở đây
                }
            });
        }

        function show_intro_video(){
            if ($('#channel_intro_url').val().trim() === '') {
                $('#channel_intro_url').hide();
                $('#channel_intro_input_file').show();
                $('#button-open-intro').hide();
            } else {
                $('#channel_intro_url').show();
                $('#channel_intro_input_file').hide();
                $('#button-open-intro').show();
            }
    
            if ($('#channel_outro_url').val().trim() === '') {
                $('#channel_outro_url').hide();
                $('#channel_outro_input_file').show();
                $('#button-open-outro').hide();
            } else {
                $('#channel_outro_url').show();
                $('#channel_outro_input_file').hide();
                $('#button-open-outro').show();
            }
    
            if ($('#channel_logo_url').val().trim() === '') {
                $('#channel_logo_url').hide();
                $('#channel_logo_input_file').show();
                $('#button-open-logo').hide();
            } else {
                $('#channel_logo_url').show();
                $('#channel_logo_input_file').hide();
                $('#button-open-logo').show();
            }
        }


        function show_Subtitle () {
            $("#text-Subtitle").text($('#channel_subtitle_text').val());
            $("#text-Subtitle").css('font-size', $('#channel_font_size').val() + 'px');
            var selectedText = $("#channel_font_text_setting option:selected").text();
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
        
    });




response = requests.get('http://127.0.0.1:50021/speakers')
data = response.json()

for iteam in data:
    Voice_language.objects.create(name=iteam['name'],speaker_uuid=iteam['speaker_uuid'])
    for style in iteam['styles']:
        syle_voice.objects.create(id_style=style['id'],name_voice=iteam['name'],style_name=style['name'],voice_language=Voice_language.objects.get(speaker_uuid=iteam['speaker_uuid']))
        


 if action == 'folder-delete':
                folder_id = request.POST.get('forder_setting')
                if folder_id:
                    ProfileChannel.objects.filter(folder_name=folder_id).delete()
                    Folder.objects.filter(id=folder_id).delete()
                    success = True
                    msg = 'Xóa Thư Mục Thành Công'

                    folder = Folder.objects.first()
                    profiles = ProfileChannel.objects.filter(folder_name=folder)
                    profile = profiles.first()
                    data = self.show_channel(folder,profile)
                    form = ProfileChannelForm(initial=data)
                    self.set_form_choices(form, profiles, profile)
                    return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
            
            if action == 'folder-update':
                folder_id = request.POST.get('forder_setting')
                folder_name = request.POST.get('input_folder_name')
                if folder_id and folder_name:
                    Folder.objects.filter(id=folder_id).update(folder_name=folder_name)
                    folder = Folder.objects.get(id=folder_id)  # get the updated Folder instance
                    success = True
                    msg = 'Cập Nhập Thư Mục Thành Công'

                    profiles = ProfileChannel.objects.filter(folder_name=folder)
                    channel = request.POST.get('channel_name')
                    try:
                        profile = ProfileChannel.objects.get(id=channel)
                    except:
                        profile = profiles.first()
                    data = self.show_channel(folder,profile)
                    form = ProfileChannelForm(initial=data)
                    self.set_form_choices(form, profiles, profile)
                else:
                    success = False
                    msg = 'Cập Nhập Thư Mục Thất Bại'
                return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})

            if action == 'add-channel':
                folder_id = request.POST.get('channel_folder_name_setting')
                channel_name = request.POST.get('input_channel_name')

                if folder_id and channel_name:
                    try:
                        folder = Folder.objects.get(id=folder_id)
                    except Folder.DoesNotExist:
                        folder = None

                    if folder:
                        # Kiểm tra xem có sự trùng lặp giữa folder và channel_name không
                        if not ProfileChannel.objects.filter(folder_name=folder, channel_name=channel_name).exists():
                            # Nếu không có trùng lặp, tạo profile mới
                            profile = ProfileChannel.objects.create(folder_name=folder, channel_name=channel_name)

                            # Cập nhật thông tin form và choices sau khi thêm profile mới
                            profiles = ProfileChannel.objects.filter(folder_name=folder)
                            data = self.show_channel(folder, profile)
                            form = ProfileChannelForm(initial=data)
                            self.set_form_choices(form, profiles, profile)

                            success = True
                            msg = 'Thêm Profile Thành Công'
                        else:
                            success = False
                            msg = 'Kênh đã tồn tại trong thư mục này'
                            form = None
                    else:
                        success = False
                        msg = 'Thư Mục Không Tồn Tại'
                        form = None
                else:
                    success = False
                    msg = 'Dữ Liệu Không Hợp Lệ'
                    form = None

                return render(request, self.template_name, {'form': form, 'success': success, 'msg': msg})





def post(self, request):
        form = ProfileChannelForm(request.POST, request.FILES)
        action = request.POST.get('action')
        channel_voice = request.POST.get('channel_voice')
        voice = syle_voice.objects.filter(voice_language=channel_voice)
        
        choices = [(voice.id_style, voice.style_name) for voice in voice]   
        form.fields['channel_voice_style'].choices = choices

        channel = request.POST.get('channel_name')
        if channel =='':
            


        form.fields['channel_name_setting'].queryset = profiles


        success = None
        msg = None

        if form.is_valid():
            if  action =='folder-add':
                folder_name = request.POST.get('input_folder_name')
                if folder_name:
                    try:
                        folder = Folder.objects.create(folder_name=folder_name)
                        success = True
                        msg = 'Thêm Thư Mục Thành Công'
                        profiles = ProfileChannel.objects.filter(folder_name=folder)
                        profile = profiles.first()
                        data = self.show_channel(folder,profile)
                        form = ProfileChannelForm(initial=data)
                    except:
                        success = False
                        msg = 'Thêm Thư Mục Thất Bại'
                    return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
                
            if action == 'folder-delete':
                folder_id = request.POST.get('forder_setting')
                if folder_id:
                    ProfileChannel.objects.filter(folder_name=folder_id).delete()
                    Folder.objects.filter(id=folder_id).delete()
                    success = True
                    msg = 'Xóa Thư Mục Thành Công'

                    folder = Folder.objects.first()
                    profiles = ProfileChannel.objects.filter(folder_name=folder)
                    profile = profiles.first()
                    data = self.show_channel(folder,profile)
                    form = ProfileChannelForm(initial=data)
                    self.set_form_choices(form, profiles, profile)
                    return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
            
            if action == 'folder-update':
                folder_id = request.POST.get('forder_setting')
                folder_name = request.POST.get('input_folder_name')
                if folder_id and folder_name:
                    Folder.objects.filter(id=folder_id).update(folder_name=folder_name)
                    folder = Folder.objects.get(id=folder_id)  # get the updated Folder instance
                    success = True
                    msg = 'Cập Nhập Thư Mục Thành Công'

                    profiles = ProfileChannel.objects.filter(folder_name=folder)
                    channel = request.POST.get('channel_name')
                    try:
                        profile = ProfileChannel.objects.get(id=channel)
                    except:
                        profile = profiles.first()
                    data = self.show_channel(folder,profile)
                    form = ProfileChannelForm(initial=data)
                    self.set_form_choices(form, profiles, profile)
                else:
                    success = False
                    msg = 'Cập Nhập Thư Mục Thất Bại'
                return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})

            if action == 'add-channel':
                folder_name = request.POST.get('channel_forder_name_setting')
                channel_name = request.POST.get('input_channel_name')
                if folder_name and channel_name:
                    folder_name = Folder.objects.get(id=folder_name)
                    if not ProfileChannel.objects.filter(folder_name=folder_name, channel_name=channel_name).exists():
                        profile = ProfileChannel.objects.create(folder_name=folder_name,channel_name=channel_name)
                        success = True
                        msg = 'Thêm profile Thành Công'
                        profiles = ProfileChannel.objects.filter(folder_name=folder)

                        data = self.show_channel(folder,profile)
                        form = ProfileChannelForm(initial=data)
                        self.set_form_choices(form, profiles, profile)
                else:
                    success = False
                    msg = 'Thêm Kênh Thất Bại'

                return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})
            

            if action == 'delete-channel':
                self.delete_channel(request)

            if action == 'update-channel':
                self.update_channel(request)

            if action == "logo-setting":
                self.edit_logo(request,form)

            if action == 'save-channel':
                self.save_channel(request)

        else:
            print(form.errors)

        return render(request, self.template_name, {'form': form ,'success': success,'msg': msg})