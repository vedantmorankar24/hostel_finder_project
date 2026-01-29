let selectedRole = '';

function showForm(role) {
    selectedRole = role;
    document.getElementById('selection-screen').classList.add('hidden');
    document.getElementById('login-form-container').classList.remove('hidden');

    const title = document.getElementById('form-title');
    const btn = document.getElementById('submit-btn');

    if (role === 'student') {
        title.innerText = "Student Portal";
        btn.className = "w-full py-4 student-gradient text-white font-black uppercase tracking-widest text-sm mt-4";
    } else if (role === 'owner') {
        title.innerText = "Owner Access";
        btn.className = "w-full py-4 owner-gradient text-white font-black uppercase tracking-widest text-sm mt-4";
    } else {
        title.innerText = "Mess Partner";
        btn.className = "w-full py-4 mess-gradient text-white font-black uppercase tracking-widest text-sm mt-4";
    }
}

