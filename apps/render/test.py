try:
            profile = ProfileChannel.objects.select_related('folder_name').get(id=pk)

            folder_id = profile.folder_name.id
            print(folder_id)
            print(profile.id)

            cache_key = f'video_render_{profile.id}'
            cached_video_url = cache.get(cache_key)

            upload_time = request.data.get('upload_time')
            upload_date = request.data.get('upload_date')
            characters = int(request.data.get('characters', 0))

            text_video = ""
            selected_videos = []

            if cached_video_url:
                videos = cached_video_url.exclude(url_video__in=selected_videos)
                if not videos.exists():
                    return JsonResponse({'error': 'No new videos available in cache'}, status=status.HTTP_404_NOT_FOUND)

                count = 1
                while len(text_video) <= characters and videos.exists():
                    video = videos.order_by('?').first()
                    selected_videos.append(video.url_video)
                    text_video += f"\n------------------------------- Video {count}  ------------------------------------------\n\n"
                    text_video += f'Url video {video.url_video} \n\n'
                    text_video += f'-----------------------------------------------------------------------------------------\n\n'
                    text_video += video.text_video
                    count += 1
                    video_url.objects.create(
                        folder_id=Folder.objects.get(id=folder_id),
                        profile_id=profile,
                        url=video.url_video  # Sửa lại chỗ này để lấy giá trị đúng
                    )
                    videos = videos.exclude(id=video.id)
                print("cache")
                # Lưu các video đã chọn vào cache
                cache.set(cache_key, videos, 30)

                if len(text_video) > characters:
                    self.cread_video_render(folder_id, profile, text_video, selected_videos, upload_time, upload_date)
                    return JsonResponse({'success': True, 'message': 'Thêm video thành công!', 'text_video': text_video}, status=status.HTTP_201_CREATED)
                else:
                    return JsonResponse({'error': 'No suitable video found'}, status=status.HTTP_404_NOT_FOUND)

            # Lấy dữ liệu từ cơ sở dữ liệu, loại bỏ các URL video rỗng và NULL
            all_data = VideoRender.objects.filter(profile_id=profile).exclude(Q(url_video_youtube='') | Q(url_video_youtube__isnull=True))

            # Chuyển đổi QuerySet thành danh sách các URL video
            results = all_data.values_list('url_video_youtube', flat=True)

            # Gộp tất cả các danh sách thành một danh sách duy nhất, loại bỏ dấu ngoặc vuông, các phần tử trống và trùng lặp
            merged_list = list(set(int(video_id) for result in results for video_id in result.strip('[]').split(',') if video_id.strip()))

            # Lọc video URL dựa trên profile_id và loại trừ những video có ID nằm trong merged_list
            url_ids = video_url.objects.filter(profile_id=profile).exclude(id__in=merged_list).values_list('url', flat=True)

            # Lọc các đối tượng DataTextVideo dựa trên folder_id và loại trừ những video có url_video nằm trong url_ids
            videos = DataTextVideo.objects.filter(folder_id=folder_id).exclude(url_video__in=url_ids)

            if not videos.exists():
                return JsonResponse({'error': 'No videos available'}, status=status.HTTP_404_NOT_FOUND)

            count = 1
            while len(text_video) <= characters and videos.exists():
                video = videos.order_by('?').first()
                selected_videos.append(video.url_video)
                text_video += f"\n------------------------------- Video {count}  ------------------------------------------\n\n"
                text_video += f'Url video {video.url_video} \n\n'
                text_video += f'-----------------------------------------------------------------------------------------\n\n'
                text_video += video.text_video
                count += 1
                videos = videos.exclude(id=video.id)
            print("search database")
            # Lưu các video đã chọn vào cache
            cache.set(cache_key, videos, 30)

            if len(text_video) > characters:
                self.cread_video_render(folder_id, profile, text_video, selected_videos, upload_time, upload_date)
                return JsonResponse({'success': True, 'message': 'Thêm video thành công!', 'text_video': text_video}, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({'error': 'No suitable video found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)