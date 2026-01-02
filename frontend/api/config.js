export default function handler(req, res) {
  res.status(200).json({
    apiUrl: process.env.API_URL
  });
}
