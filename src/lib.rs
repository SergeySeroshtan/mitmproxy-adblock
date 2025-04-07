use pyo3::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn sum_as_string(a: usize, b: usize) -> PyResult<String> {
    Ok((a + b).to_string())
}

#[pyfunction]
fn print_name(obj: &Bound<'_, PyAny>) -> PyResult<()> {
    let name = obj.getattr("name")?;
    println!("Name: {}", name);
    Ok(())
}

/// A Python module implemented in Rust.
#[pymodule]
fn mitmproxy_adblock(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(print_name, m)?)?;
    Ok(())
}
