if (process.env.NEXT_MANUAL_SIG_HANDLE) {
    process.on('SIGTERM', () => {
        console.log('Received SIGTERM: cleaning up')
        process.exit(0)
    })
    process.on('SIGINT', () => {
        console.log('Received SIGINT: cleaning up')
        process.exit(0)
    })
}