/**
 * Test Upload Langsung ke Backend (tanpa Next.js proxy)
 */

const fs = require('fs');
const path = require('path');
const FormData = require('form-data');
const axios = require('axios');

const BASE_URL = 'http://localhost:8001/api/v1';
const TEST_CREDENTIALS = {
  username: 'testuser2',
  password: 'testpass123'
};

async function testUploadDirect() {
  console.log('🧪 Test Upload Langsung ke Backend...\n');

  try {
    // 1. Login
    console.log('1️⃣ Login...');
    const loginRes = await axios.post(`${BASE_URL}/auth/login`, TEST_CREDENTIALS);
    const { access_token } = loginRes.data.data;
    console.log('✅ Logged in!');

    // 2. Upload
    console.log('2️⃣ Upload MP4...');
    const testFile = path.join(__dirname, 'test-720p.mp4');
    
    const form = new FormData();
    form.append('title', 'TEST UUID UPLOAD');
    form.append('file', fs.createReadStream(testFile));
    form.append('channel_id', '2');
    form.append('category', 'entertainment');
    form.append('description', 'Testing UUID filename generation');

    const uploadRes = await axios.post(`${BASE_URL}/videos/upload`, form, {
      headers: {
        ...form.getHeaders(),
        'Authorization': `Bearer ${access_token}`
      },
      maxBodyLength: Infinity,
      maxContentLength: Infinity
    });

    console.log('\n✅ Upload successful!');
    console.log('\n📊 Response:');
    console.log(JSON.stringify(uploadRes.data, null, 2));

    // 3. Cek UUID filename
    console.log('\n3️⃣ Checking UUID filename...');
    const video = uploadRes.data.data;
    console.log(`   youtube_id (UUID): ${video.youtube_id}`);
    console.log(`   thumbnail: ${video.thumbnail_url}`);

    // 4. Test thumbnail access
    console.log('\n4️⃣ Testing thumbnail access...');
    try {
      const thumbRes = await axios.get(`http://localhost:8001${video.thumbnail_url}`, {
        responseType: 'arraybuffer'
      });
      console.log(`   ✅ Thumbnail accessible! (${thumbRes.data.length} bytes)`);
    } catch (e) {
      console.log(`   ❌ Thumbnail error: ${e.message}`);
    }

    console.log('\n✅ SUCCESS: UUID filename works!');

  } catch (error) {
    console.error('\n❌ TEST FAILED!');
    if (error.response) {
      console.error(`Status: ${error.response.status}`);
      console.error(`Response:`, JSON.stringify(error.response.data, null, 2));
    } else {
      console.error(error.message);
    }
    process.exit(1);
  }
}

testUploadDirect();
