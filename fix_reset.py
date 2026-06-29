import os

# 1. Create the 'registration' folder inside 'templates'
os.makedirs('templates/registration', exist_ok=True)

# 2. Define the 4 files and their premium HTML content
files = {
    'templates/registration/password_reset.html': """{% extends 'base.html' %}
{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-slate-100">
    <div class="max-w-md w-full">
        <div class="text-center mb-8">
            <h2 class="text-3xl font-bold text-slate-900">Reset Password</h2>
            <p class="mt-2 text-slate-600">Enter your email to receive a secure reset link.</p>
        </div>
        <div class="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
            <form method="POST" class="space-y-6">
                {% csrf_token %}
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-2">Email Address</label>
                    <input type="email" name="email" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition" placeholder="you@example.com">
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold py-4 rounded-xl shadow-lg hover:shadow-xl transition-all">Send Reset Link</button>
            </form>
            <div class="mt-6 text-center">
                <a href="{% url 'login' %}" class="text-sm font-bold text-indigo-600 hover:text-indigo-700 transition">Back to Login</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/registration/password_reset_done.html': """{% extends 'base.html' %}
{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-slate-100">
    <div class="max-w-md w-full text-center">
        <h2 class="text-3xl font-bold text-slate-900 mb-2">Check your inbox</h2>
        <p class="text-slate-600 mb-8">If an account exists with that email, we have sent password reset instructions. <br><strong>(Check your VS Code terminal for the link!)</strong></p>
        <a href="{% url 'login' %}" class="text-sm font-bold text-indigo-600 hover:text-indigo-700 transition">Return to Login</a>
    </div>
</div>
{% endblock %}""",

    'templates/registration/password_reset_confirm.html': """{% extends 'base.html' %}
{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-slate-100">
    <div class="max-w-md w-full">
        <div class="text-center mb-8">
            <h2 class="text-3xl font-bold text-slate-900">Create New Password</h2>
        </div>
        <div class="bg-white rounded-2xl shadow-xl border border-slate-200 p-8">
            {% if validlink %}
            <form method="POST" class="space-y-6">
                {% csrf_token %}
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-2">New Password</label>
                    <input type="password" name="new_password1" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition">
                </div>
                <div>
                    <label class="block text-sm font-semibold text-slate-700 mb-2">Confirm New Password</label>
                    <input type="password" name="new_password2" required class="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition">
                </div>
                <button type="submit" class="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-bold py-4 rounded-xl shadow-lg hover:shadow-xl transition-all">Reset Password</button>
            </form>
            {% else %}
            <div class="text-center">
                <p class="text-red-600 font-semibold mb-4">This password reset link is invalid or has expired.</p>
                <a href="{% url 'password_reset' %}" class="text-sm font-bold text-indigo-600 hover:text-indigo-700 transition">Request a new link</a>
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}""",

    'templates/registration/password_reset_complete.html': """{% extends 'base.html' %}
{% block content %}
<div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-slate-100">
    <div class="max-w-md w-full text-center">
        <h2 class="text-3xl font-bold text-slate-900 mb-2">Password Reset Complete!</h2>
        <p class="text-slate-600 mb-8">Your password has been successfully changed.</p>
        <a href="{% url 'login' %}" class="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all">Go to Login</a>
    </div>
</div>
{% endblock %}"""
}

# 3. Write the files to the disk
for path, content in files.items():
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created {path}")

print("\n🎉 All 4 password reset files created successfully!")