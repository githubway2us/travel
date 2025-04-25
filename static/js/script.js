function addActivity() {
    const container = document.getElementById('activities');
    const newActivity = document.createElement('div');
    newActivity.className = 'activity row mb-3';
    newActivity.innerHTML = `
        <div class="col-md-2">
            <label for="time" class="form-label">เวลา</label>
            <input type="time" class="form-control" name="time" step="900">
        </div>
        <div class="col-md-4">
            <label for="detail" class="form-label">รายละเอียด</label>
            <input type="text" class="form-control" name="detail">
        </div>
        <div class="col-md-2">
            <label for="budget" class="form-label">งบ (บาท)</label>
            <input type="number" class="form-control" name="budget" step="0.01">
        </div>
        <div class="col-md-4">
            <label for="image" class="form-label">รูปภาพ</label>
            <input type="file" class="form-control" name="image" accept="image/*">
        </div>
    `;
    container.appendChild(newActivity);
}