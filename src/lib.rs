use pyo3::prelude::*;

#[derive(FromPyObject, Debug)]
struct PyPerson {
    name: String,
}

#[pyfunction]
fn print_name(person: PyPerson) -> PyResult<String> {
    println!("Got person: {:?}", person);
    Ok(person.name)
}

/// A Python module implemented in Rust.
#[pymodule]
fn mitmproxy_adblock(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add_function(wrap_pyfunction!(print_name, m)?)?;
    Ok(())
}
