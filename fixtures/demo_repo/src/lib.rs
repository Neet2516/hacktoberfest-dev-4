pub fn parse_config(raw: &str) -> Result<String, &'static str> {
    if raw.is_empty() {
        return Err("Configuration cannot be empty");
    }
    Ok(raw.to_uppercase())
}
