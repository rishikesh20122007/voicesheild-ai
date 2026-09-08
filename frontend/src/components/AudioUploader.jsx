function AudioUploader({ file, onFileChange }) {
  const handleChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      onFileChange(selected);
    }
  };

  return (
    <div>
      <label className="block text-sm text-slate-300 mb-2">Upload Audio File</label>
      <input
        type="file"
        accept=".wav,.mp3,.m4a,.flac,.ogg"
        onChange={handleChange}
        className="block w-full text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-vs-accent file:text-vs-dark file:font-semibold hover:file:bg-cyan-300"
      />
      {file && (
        <p className="text-slate-400 text-sm mt-2">Selected: {file.name}</p>
      )}
    </div>
  );
}

export default AudioUploader;
