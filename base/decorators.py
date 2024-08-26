from django.shortcuts import redirect

def check_access(allowed_users:list=[], admin_only:bool=False, feature:str=None):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_authenticated:
                # Admin God Access
                if request.user.username == 'admin':
                    return view_func(request, *args, **kwargs)
                
                # Admin Only Access
                if admin_only:
                    if request.user.username != 'admin':
                        return redirect('product-types')

                    else:
                        return view_func(request, *args, **kwargs)
                
                # Check if user has created profile
                if request.user.user_profile.first_name == '' or request.user.user_profile.first_name == None and feature != 'create-profile':
                    return redirect('create-profile')
                
                # If allowed roles are provided, check if user has the required role
                if allowed_users:
                    if request.user.user_profile.user_type in allowed_users:
                        return view_func(request, *args, **kwargs)
                    else:
                        return redirect('product-types')
                else:
                    return view_func(request, *args, **kwargs)
            else:
                if feature == 'handles-page' or feature == 'home':
                    return view_func(request, *args, **kwargs)
                else:
                    return redirect('user-signin')
        return wrapper_func
    return decorator